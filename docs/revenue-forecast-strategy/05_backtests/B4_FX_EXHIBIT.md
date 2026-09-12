# B4 — the FX exhibit: both live 3Q26 numbers, the four-way reconciliation, the lag rule for the guide, and the observed shares on data through today

Package: `analysis/src/forecast_methods/fx_lag_v2/` (a COPY of `fx_lag/`, modified; nothing in `fx_lag/` is touched)
Data: `data/processed/forecast_methods/fx_lag_v2/`
Registry: `fx-lag-v2__fx_pts_revenue_2026q4_v2`, `fx-lag-v2__fx_rev_next_q_h2_v2` (both NEW files)
Run date 2026-09-11. FX refreshed from FRED this morning; **the refresh reaches 2026-09-04**, because H.10 publishes with about a week's lag. Every "as of today" number below is FX through 4 Sep and is labelled so. Harness format v1.0 (frozen) obeyed; `harness/score.py` NOT run.

## Exact commands

```bash
cd "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB"
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/fx_lag_v2/fetch_fx_v2.py   # refresh, ~10 s
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/fx_lag_v2/run.py           # exit 0, ~25 s
```

---

## 0. The one-paragraph answer

**Both live 3Q26 numbers are right about different objects, and the exhibit's job is to say which.** On data through 4 September the free fit — the specification the programme registered — puts 3Q26 revenue FX at **+1.3pp** (80% band −0.1 to +2.6). The architect's Φ kernel at the free fit's own scale of 0.851 puts it at **+2.9pp**. Management, on 6 August, guided "an approximate **three** percentage point FX tailwind after factoring in our hedging program". The difference is not a data disagreement: the two specifications see the same three basket numbers (1Q26 +5.67%, 2Q26 +2.27%, 3Q26 +0.43% QTD) and disagree only about **when** a basket move reaches revenue. The free fit loads 53% on the quarter of check-in; the Φ kernel loads nothing there. On the full 14-quarter sample the free fit wins and Φ is rejected (LR 10.2, p 0.017 stated; 16.8, p 0.0008 gross) — that result is unchanged by the refresh, because the refresh only moves a quarter that is not in the sample. On the last three quarters, and against management's own quantification, Φ at 0.851 wins by a factor of five. **n = 3. That is a hypothesis, and 5 November is its test.** For the object the memo actually needs — what management will *state* for Q4 on 5 November — the lag-loaded spec is the right one regardless of which is the better description of the world, because at a guide date only 32–38% of the guided quarter's FX has printed. Under it, 4Q26 revenue FX is **+1.0pp** (confidence-set interval +0.3 to +2.2; 80% predictive band −0.3 to +2.3), against the repo bridge's −3.4pp step, the repo schedule's −0.4pp and the guide-anchored +2.6pp — a 6.0pp spread worth **$167M** of 4Q26 revenue.

---

## 1. The refresh — what moved, and what did not

`fetch_fx_v2.py` is `analysis/src/overnight/10_fetch_fx.py` with three changes and no others: the output path (it writes `fx_daily_2026-09-11.csv` / `fx_quarterly_2026-09-11.csv` under `forecast_methods/fx_lag_v2/`, never `10_fx_daily.csv`), **DTWEXBGS broad USD** added alongside the nine bilaterals (as an index level, carrying `unit='index_level_usd_strength'`, so downstream code cannot mistake it for a price), and a fetch manifest.

All ten series last print **2026-09-04**. Prior file ended 2026-08-28, so the refresh adds five business days.

| series | 3Q26 y/y to 28 Aug | 3Q26 y/y to 4 Sep | series | 3Q26 y/y to 28 Aug | 3Q26 y/y to 4 Sep |
|---|---|---|---|---|---|
| EUR | −1.56 | **−1.46** | AUD | +7.49 | **+7.73** |
| GBP | −0.17 | **−0.11** | KRW | −4.08 | **−3.44** |
| BRL | +6.18 | **+6.18** | JPY | −8.17 | **−8.01** |
| MXN | +7.87 | **+8.08** | INR | −8.72 | **−8.63** |
| CAD | −1.68 | **−1.56** | **USD broad** | −0.39 | **−0.51** |

Quarterly revenue-weighted basket, rebuilt (`02_basket_quarterly.csv`). **Only 3Q26 moves**; every completed quarter is identical to the prior build to the third decimal, which is the check that the refresh changed nothing it should not have:

| quarter | NA | EMEA | LatAm | APAC | **global** (28 Aug → 4 Sep) |
|---|---|---|---|---|---|
| 3Q25 | −0.05 | +5.37 | +1.53 | −1.61 | +2.04 → **+2.04** |
| 4Q25 | +0.22 | +7.34 | +8.16 | −0.56 | +3.65 → **+3.65** |
| 1Q26 | +0.70 | +9.51 | +12.36 | +4.91 | +5.67 → **+5.67** |
| 2Q26 | +0.25 | +1.93 | +11.44 | +2.73 | +2.27 → **+2.27** |
| **3Q26 QTD** | +0.04 | −1.05 | +6.47 | +1.70 | +0.36 → **+0.43** |

Reconciliation against the published `10_fx_basket.csv` (`03_basket_reconciliation.csv`): 1Q26 and 2Q26 reproduce to under 0.008pp on all four regional baskets and to 0.076pp on the global (the 0.08pp gap is the unpublished regional revenue weights, unchanged from `fx-lag`); the 3Q26 rows differ by 0.02–0.23pp **because of the refresh**, which the file states in a `note` column rather than leaving as an apparent failure.

**Observed-to-date share of the quarter**, from real FRED prints (`19_baskets_spot_held_v2.csv`): **3Q26 = 0.712** of its business days are printed at 4 Sep (calendar-elapsed at 11 Sep is 0.783); **4Q26 = 0.000**. Completing 3Q26 at spot held constant from 4 Sep gives a full-quarter basket of **+0.60%**; 4Q26 entirely at held spot gives **+1.35%**, which is *higher* than 3Q26 — the dollar is weaker against BRL/MXN/AUD relative to the 4Q25 comparison base than it was against the 3Q25 base.

**A fix inherited from `fx_lag` and corrected here.** `fx_lag/pit_fx._q_avg_spot_held` filled every business day with no FRED print — US bank holidays inside long-completed quarters included — with the *current* spot, so a 2026 rate entered 2025 quarterly averages on two or three days out of about sixty-four. v2 fills a missing day with the last rate observed on or before it and holds spot only after the last observation. This moves the basket-driven PIT specs by 0.1–0.3pp of RMSE (H0 W1 1.77 → 1.88, H3 W1 1.49 → 1.59) and leaves **H2 exactly unchanged** (W1/W2 RMSE 0.9936, bias +0.0975, interval RMSE 0.5782, n = 10), because H2's driver is the disclosed ADR-FX point rather than the basket.

---

## 2. The already-observed share — the triple, at four decision dates

`20_observed_share_triple.csv`. Definition, unchanged from `00_IMPLEMENTATION_DECISIONS` §2.4:

```
FX-determined share = w1 + w2 + w0 x f        f = share of the target quarter already in the average
```

Three specifications, **always together**: (a) the free fit (Object A, refreshed; stated w0 = 0.53, gross w0 = 0.57), (b) the Φ kernel (0, ⅔, ⅓), (c) contemporaneous (1, 0, 0). Two readings of `f`: calendar days elapsed (the programme's existing convention, and the one that reproduces M6's 0.54) and FRED business days actually printed, allowing the H.10 one-week publication lag. Volume-determined share alongside.

| date | target | f, calendar | f, FRED prints | **(a) free fit** (CS band) | **(b) Φ kernel** | **(c) contemporaneous** | **volume-determined** |
|---|---|---|---|---|---|---|---|
| **2026-08-06** 3Q26 guide | 3Q26 | 0.391 | 0.379 | **0.68** [0.39, 1.00] | **1.00** | **0.39** | 1.00 |
| **2026-09-11** today | 3Q26 | 0.783 | 0.712 | **0.88** [0.78, 1.00] | **1.00** | **0.78** | 1.00 |
| 2026-10-02 pitch date | 4Q26 | 0.011 | 0.000 | **0.47** [0.01, 1.00] | **1.00** | **0.01** | **0.333** |
| **2026-11-05** 4Q26 guide | 4Q26 | 0.380 | 0.318 | **0.67** [0.38, 1.00] | **1.00** | **0.38** | **1.00** |
| **2027-02-11** 1Q27/FY27 guide | 1Q27 | 0.456 | 0.391 | **0.71** [0.46, 1.00] | **1.00** | **0.46** | 1.00 |

Read off the FRED-print column instead and every free-fit number falls by 2–4pp (5 Nov: 0.67 → 0.64; today: 0.88 → 0.85) and every contemporaneous number by 6pp. The gap between the calendar and the data is the publication lag, and it is the one part of "already observed" that is a fact rather than a modelling choice.

**Three sentences that must travel together.**

1. **At the 5 November guide date the FX-determined share of 4Q26 is 0.67 on the free fit, 1.00 on the Φ kernel and 0.38 contemporaneous.** M6's λ = 0.75 gives 0.54 and sits inside the free fit's band — reproduced exactly, and it is the pessimistic end, not the estimate. The honest single sentence is *"between 38% and 100%, and which end you believe is the whole of the lag argument"*.
2. **Volume-determined share at 5 November is 1.00.** 3Q26 GBV prints that morning, so the kernel base ⅔·GBV(3Q26) + ⅓·GBV(2Q26) is fully known. This is the defensible claim and it does not depend on the lag at all.
3. **Volume-determined share at the 2–24 October pitch date is 0.333.** Only 2Q26 GBV has printed; 3Q26 GBV, which carries two-thirds of the weight, has not. The asymmetry must be said out loud in the pitch. Note the FX asymmetry runs the *other* way at that date: 0.011 of the 4Q26 quarter has elapsed, so on the contemporaneous reading essentially none of 4Q26's FX is fixed while on the Φ reading all of it is. **The 82% figure and the "85–90% on the booking ledger" figure are not used anywhere in this package.**

---

## 3. The live 3Q26 exhibit — three numbers in one table

`21_live_3q26_three_numbers.csv`. Basket inputs: 3Q26 +0.595% (QTD to 4 Sep, spot held), 2Q26 +2.266%, 1Q26 +5.673%; Φ driver ⅔·b(2Q26) + ⅓·b(1Q26) = **+3.402%**.

| construction | weights | basis | **3Q26 FX, pp** | 80% band |
|---|---|---|---|---|
| **ours — Object-A free fit, stated series (PIT-clean)** | (0.45, 0.36, 0.03) | after hedge | **+1.3** | −0.1 to +2.6 |
| ours as registered by `fx-lag` — free fit, gross weights | (0.54, 0.41, 0.00) | gross | **+1.2** | +0.1 to +2.4 |
| **Φ kernel (0, ⅔, ⅓) × 0.851** (the free fit's own total scale) | (0, 0.57, 0.28) | after hedge | **+2.9** | +1.6 to +4.2 |
| Φ kernel × 0.653 (scale fitted to the Φ *shape*, stated) | (0, 0.44, 0.22) | after hedge | +2.2 | — |
| Φ kernel × 0.721 (same, gross) | (0, 0.48, 0.24) | gross | +2.4 | — |
| Φ kernel × 0.56 (architect's literal H0) | (0, 0.37, 0.19) | gross | +1.9 | — |
| contemporaneous × 0.56 | (0.56, 0, 0) | gross | +0.3 | — |
| **MANAGEMENT, 6 Aug letter** — "approximately three percentage points of FX tailwind after factoring in our hedging program" | — | **after hedge, as stated** | **+3.0** | — |
| management implied gross (stated + 0.21pp hedge drag, applied ONCE) | — | gross, derived | +3.2 | — |

Two honest notes on the middle rows. The **0.851** scale is the free fit's *total* scale re-assigned onto the Φ shape — it is a construction, not a fitted object, and it is the one `RED_TEAM` F4 validated on the three live quarters. The scale fitted to the Φ shape by itself is **0.653** (LR 9.87, p 0.0072 against the free fit, so the shape is still rejected in-sample even with a free scale). The two differ by 0.7pp on 3Q26 and 0.22pp on 4Q26. Both are shown; neither is hidden behind the other.

### 3.1 The hedge line, shown once

`22_hedge_gross_vs_after.csv`. The identity `gross_ex_hedge + hedge_effect = stated` holds on all 14 quarters to 1e-6.

| quarter | designated notional $m | reclassified to revenue $m | hedge, pp of growth | **stated FX pp** | **gross FX pp** |
|---|---|---|---|---|---|
| 3Q25 | 2,600 | −42 | **−1.13** | 0 | +1.13 |
| 4Q25 | 3,100 | −23 | **−0.93** | +1 | +1.93 |
| 1Q26 | 3,300 | −15 | **−0.66** | +3 | +3.66 |
| 2Q26 | 3,400 | −19 | **−0.61** | +4 | +4.61 |
| 3Q26–2Q27 (forward, from the 2Q26 10-Q's ~$26M) | — | — | **−0.21 / −0.21 / −0.18 / −0.18** | — | — |

**The hedge-once rule, for the record: the letter-stated revenue-FX points are ALREADY AFTER hedges.** `28_fx_hedge_forward.csv` is never added on top of a letter-stated point. It appears exactly once in this package — converting management's stated +3.0 into an implied gross +3.2 in the table above — and the forward schedule in §4 is on the same after-hedge basis as the stated target it was fitted to, so it needs no further adjustment. Hedges are on the **loss** side and cannot be the source of the tailwind; any note that says otherwise is wrong.

### 3.2 The regime paragraph — and the 5 November test, pre-registered

**Full sample, the lag is short.** On 14 letter-rounded observations scored as intervals, the effective lag of the stated revenue-FX contribution is **0.50 quarters** (95% CS 0.00–1.19), weight on lag 2 is **0.04**, and the Φ restriction is rejected (LR 10.2, p 0.017; free-scale variant LR 9.87, p 0.0072). On the gross series the lag is 0.43 quarters (CS 0.03–0.92) and Φ is rejected at p 0.0008. Theo's pure two-quarter lead is the hardest-rejected restriction of the five (p 0.0004 stated, p < 0.0001 gross). None of this moved with the refresh.

**The last three quarters, and management's own quantification, favour the lagged kernel.** 1Q26 actual +3, 2Q26 actual +4, 3Q26 management ~+3: the free fit gives 3.97 / 3.20 / 1.26 (mean absolute error **1.20pp**), Φ × 0.851 gives 2.71 / 4.25 / 2.89 (mean absolute error **0.22pp**). The free fit is worst on the quarter that is nearly observed, and it is worst in the direction of saying management is wrong about their own quarter.

**n = 3. This is a hypothesis, not a result.** Three observations cannot overturn an interval-likelihood rejection at n = 14, and one of the three is a management forecast rather than a print. The two facts coexist and the memo must carry both.

**The test, stated in advance.** On 5 November Airbnb prints 3Q26 and states the realised revenue-FX contribution as a letter-rounded integer. Predictions, made today on FX through 4 September:

| spec | 3Q26 point | letter integer it implies |
|---|---|---|
| contemporaneous × 0.56 | +0.3 | **0** |
| free fit, stated (registered by `fx-lag`) | +1.3 | **+1** |
| Φ × 0.653 / Φ × 0.56 | +2.2 / +1.9 | **+2** |
| **Φ × 0.851 (and management's guide)** | **+2.9** | **+3** |

**Decision rule: a printed 3Q26 revenue-FX of +3 or more supports the lag-loaded kernel and closes the argument in the architect's favour; 0 or +1 supports the free fit and means the +1.2pp the programme registered was right and management's guide was conservative; +2 is the ambiguous middle and should be reported as ambiguous.** No number in this table is revised after 5 November to fit the print.

---

## 4. The forecast rule for the GUIDE, and the 4Q26 object

**The rule.** Use the lag-loaded spec (H2 / Φ) for anything that asks *what management will say*, and for the 4Q26 revenue-FX contribution. The reason is mechanical, not aesthetic: at a guide date roughly 32–38% of the guided quarter's FX has printed (§2), so a lag-0 loading is a forecast of something nobody can see. This is exactly why H2 is the best point-in-time forecaster in the horse race (`09c_pit_window_scores.csv`, unchanged by the refresh): **W1 and W2 RMSE 0.99pp, MAE 0.90pp, bias +0.10, interval RMSE 0.58**, against 1.59–1.88 for the free fit and 1.88–1.97 for the contemporaneous spec — and it is the one spec whose PIT and full-sample replays coincide (mean absolute point delta 0.22pp, max 0.50pp over 11 matched rows), so its backtest is not borrowing from the future. Say **"best, within noise"**: at n = 10 the standard error of an RMSE is 0.2–0.3pp. H2 covers 10 of 14 W1 quarters (its driver, the disclosed ADR-FX point, starts 2Q22), so under the survives-both-windows rule it is **not quotable as a W1 winner**; that is unchanged and is a property of the data.

**The 4Q26 object** (`23_forecast_4q26_v2.csv`), spot held constant from 2026-09-04:

| | 3Q26 | **4Q26** | 1Q27 | 2Q27 | 3Q27 | 4Q27 |
|---|---|---|---|---|---|---|
| basket lag 0 / lag 1 / lag 2, % | 0.60 / 2.27 / 5.67 | **1.35 / 0.60 / 2.27** | 0.41 / 1.35 / 0.60 | 0.34 / 0.41 / 1.35 | 0.50 / 0.34 / 0.41 | 0.00 / 0.50 / 0.34 |
| Φ driver, % | 3.40 | **1.15** | 1.10 | 0.73 | 0.36 | 0.44 |
| **point, Φ × 0.851** | +2.9 | **+1.0** | +0.9 | +0.6 | +0.3 | +0.4 |
| point, Φ × 0.653 | +2.2 | +0.8 | +0.7 | +0.5 | +0.2 | +0.3 |
| point, Φ on ADR-FX (H2 proper) | +2.9 | +0.9 | +0.9 | +0.6 | +0.2 | +0.3 |
| point, free fit (for contrast) | +1.3 | +0.9 | +0.7 | +0.3 | +0.4 | +0.2 |
| **interval from the 95% lag confidence set** | +0.3 to +3.5 | **+0.3 to +2.2** | +0.2 to +1.2 | +0.2 to +1.0 | +0.2 to +0.6 | 0.0 to +0.4 |
| 80% predictive band (σ = 1.03pp) | +0.9 to +3.5 | **−0.3 to +2.3** | −0.6 to +2.0 | −0.8 to +1.8 | −1.1 to +1.6 | −1.0 to +1.6 |

Under ±1 sd parallel dollar paths (±5% on the held spot, about one standard deviation of a two-quarter move):

| path | 3Q26 | **4Q26** | 1Q27 | 2Q27 | **FY27, revenue-weighted average** |
|---|---|---|---|---|---|
| weak USD (+5%) | +2.9 | **+1.5** | +2.9 | +3.2 | **+2.8** |
| **spot held** | **+2.9** | **+1.0** | **+0.9** | **+0.6** | **+0.5** |
| strong USD (−5%) | +2.9 | **+0.5** | −1.0 | −1.9 | **−1.8** |

3Q26 barely moves under the scenarios because 71% of it has printed; 4Q26 moves ±0.5pp and FY27 moves +2.3 / −2.3pp. **The dollar path dominates FY27 FX and is worth more than any decomposition line in it.**

**Two arithmetic warnings.** (i) An FY27 y/y FX contribution is the revenue-weighted **average** of its four quarterly contributions, never their sum: 0.93 + 0.62 + 0.31 + 0.38 = 2.24, ÷ 4 = +0.56, revenue-weighted on 2025 actual quarterly shares = **+0.52pp**. `23b_fy27_annualisation_v2.csv` carries the sum in a column named `sum_of_four_quarters_pp_DO_NOT_QUOTE`. (ii) **4Q27 is mechanically 0.00% on the basket under spot held**, because both the quarter and its base are entirely held at the same rate. That is a property of the scenario, not a forecast.

**Forward curve: NOT DERIVABLE.** The FRED endpoint carries spot bilaterals and DTWEXBGS only — no forward points, no FX futures, no non-USD rate differentials. The scenario set is spot-held plus a parallel shift, and the forward-curve path is reported unavailable rather than fabricated.

### 4.1 Registry

| file | rows | target | window | vintage | prior bases | free params |
|---|---|---|---|---|---|---|
| `fx-lag-v2__fx_pts_revenue_2026q4_v2.csv` | 2 | `fx_pts_revenue` 2026Q4 | LIVE | 2026-09-11 | PIT + full_sample | 2 (scale, σ) |
| `fx-lag-v2__fx_rev_next_q_h2_v2.csv` | 40 | `fx_pts_revenue` | W1 (10/14), W2 (10/10) | 14 guide dates | PIT + full_sample | 2 |

The live row: **point +0.98, q10 −0.34, q50 +0.98, q90 +2.30, sd 1.027, `knowable_from` 2026-09-04, `spec_id` `H2_phi_kernel_on_basket_scale_0.851_spot_held_2026-09-04`.** The band written to the quantile ladder is the *predictive* band; the wider confidence-set interval (+0.31 to +2.16) is carried in `notes` and in `23_forecast_4q26_v2.csv`, because the frozen format has one ladder per row and the scorer reads it as a predictive distribution. The `full_sample` replay is byte-identical to the PIT replay **by construction** — for a LIVE object the point-in-time information set *is* the full sample — and the row says so rather than presenting the coincidence as agreement. No consensus number is consumed, so `street_vendor` / `street_as_of` are correctly absent.

**Harness change request (unchanged from `fx-lag`, re-confirmed).** `windows.csv` admits only 2026Q3 as a LIVE target, so `validate_registry_frame(strict_windows=True)` refuses `window=LIVE, quarter=2026Q4` with *"that quarter belongs to []"*. The refusal was triggered, printed and recorded; the row was then registered through the harness's own `register()` with `strict_windows=False` and **every other rule enforced strictly** (vintage in the guide calendar, PIT rule, quantile monotonicity, frozen column set). Requested: admit `LIVE` for any quarter ≥ 2026Q3, or add a `FORWARD` window. **Second request, also unchanged: there is no annual target in `targets.csv`**, so FY27 FX cannot be registered as a row and is reported here and in `23b` as a revenue-weighted average of four quarterly objects.

---

## 5. The four-way reconciliation

`24_four_way_4q26.csv`. **This is the only place the rejected constructions appear, and this package emits no additive FX pp to revenue.** One column distinguishes a *level* (pp of y/y in the quarter) from a *step applied in a walk* — the `fx-lag` note put both in one column, and the distinction is exactly where the double-subtraction lives. $27.8M per pp on 4Q25 revenue of $2,778M.

### 5.1 4Q26

| construction | level, pp | step in a walk | status | named cause | vs adopted |
|---|---|---|---|---|---|
| repo `29_q4_fy27_bridge` FX step | −0.4 | **−3.4** | REJECTED | the *level* it carries is the `05_fx_schedule` fit; the **−3.4pp is that level subtracted from a guide-anchored walk whose 3Q26 start already contains management's +3.0pp**, and from a GBV base already in booking-date USD. Double subtraction, twice over | −1.4pp, **−$39M** |
| repo `05_fx_schedule` `revenue_fx_fit_pp` | **−0.4** | — | REJECTED | a reduced-form level fit on a lagged EURUSD / broad-USD blend. EURUSD is not the basket: EUR y/y ran +11.1 (1Q26) → −1.5 (3Q26) while LatAm (+6.5) and APAC (+1.7) held the basket up. It also re-applies a lag already inside the lagged GBV base | −1.4pp, **−$39M** |
| M6 memo forward schedule (after hedge; +0.62 gross) | **+0.4** | — | REJECTED | a contemporaneous two-index construction (λ = 0.75) that misses a nearly observed 3Q26 by ~2pp; M6's own note carries +1.04pp in its schedule against +0.73pp in its 3Q26 build | −0.6pp, **−$16M** |
| guide-anchored (hold +3.0pp flat) | **+2.6** | — | REJECTED | holds the 3Q26 tailwind into 4Q26. The basket itself rolls over (1Q26 +5.7 → 2Q26 +2.3 → 3Q26 +0.4), so flat imports a tailwind the spot path has already removed | +1.6pp, **+$45M** |
| **kernel-implied: Φ × 0.851 on the refreshed basket, spot held** | **+1.0** | 0.0 | **ADOPTED, as an OUTPUT** | booking-date FX is already inside the lagged USD GBV base; the pp shown is what the arithmetic produces and is never applied to a revenue forecast. Φ × the 0.653 shape-scale gives +0.75pp | — |

**Spread on levels: −0.4 to +2.6 = 3.0pp = $84M.** Including the bridge's −3.4pp step: **6.0pp = $167M.** The internal disagreement about FX alone is larger than the gap between our 4Q26 number and the Street's, and saying so first is a point in our favour.

### 5.2 FY27

`25_four_way_fy27.csv`. 1pp of FY27 growth = 1% of FY26 revenue; FY26 base **$14,293M** (1Q26 $2,678M + 2Q26 $3,608M actual + 3Q26 $4,816M, the programme's guide × cushion number + 4Q26 $3,191M at the frozen card), so **$142.9M per pp**.

| construction | level, pp | step in a walk | status | named cause | vs adopted |
|---|---|---|---|---|---|
| repo `29` bridge FY27 | −0.6 | **−3.4** | REJECTED | the same double subtraction one year out: the −3.4pp step comes off an FY26 base that already carries FY26's +2.7pp of stated FX | −1.1pp, **−$160M** |
| repo `05_fx_schedule`, revenue-weighted average 1Q27–4Q27 | **−0.6** | — | REJECTED | the same EURUSD-only reduced form, annualised; it has FX turning materially negative through FY27 where the revenue-weighted basket only fades | −1.1pp, **−$162M** |
| M6 rule (λ = 0.75) reconstructed on the refreshed basket — **our reconstruction, not an M6 number**; the M6 table stops at 2Q27 | +0.2 | — | REJECTED | contemporaneous-dominant weighting of a basket nobody can observe a year out: a spot forecast wearing a lag's clothes | −0.3pp, **−$42M** |
| guide-anchored (hold +3.0pp flat) | **+3.0** | — | REJECTED | imports a 2026 dollar path into 2027; under spot held the basket y/y is near zero by 2Q27 *by arithmetic*, because the base quarters are themselves recent | +2.5pp, **+$354M** |
| **kernel-implied: Φ × 0.851, revenue-weighted average** | **+0.5** | 0.0 | **ADOPTED, as an OUTPUT** | the FY27 contribution is the revenue-weighted average of four quarterly outputs of the lagged-GBV arithmetic; the SUM is meaningless. Φ × 0.653 gives +0.40pp | — |

**Spread: −0.6 to +3.0 = 3.6pp = $516M of FY27 revenue.** Against that, the ±1 sd dollar path alone is worth +2.8 / −1.8pp = **$657M** — so the FY27 FX decomposition argument is smaller than the FY27 FX *risk*, and the memo should say the dollar, not the method, is what it is exposed to.

---

## 6. Booking-date FX through Φ, and the ex-FX step

`27_kernel_carried_fx_v2.csv`, all one decimal, recomputed from the refreshed basket. The 3Q26 ADR-FX point is not yet disclosed and is fitted from the contemporaneous basket (slope 0.872, intercept −0.076, r 0.962, n = 14) at **+0.4**.

| reading | 3Q26 | 4Q26 | **step** |
|---|---|---|---|
| A: disclosed ADR-FX through Φ (the architect's construction) | +2.5 | +0.7 | **−1.8** |
| B: basket × 0.56 through Φ | +1.9 | +0.6 | −1.3 |
| **C: Φ × 0.851 (ADOPTED)** | **+2.9** | **+1.0** | **−1.9** |
| C2: Φ × 0.653 | +2.2 | +0.8 | −1.5 |
| D: Object-A free weights on the basket | +1.3 | +0.9 | −0.4 |

Reading A lands at +2.5 / +0.7 / −1.8 against the architect's stated +2.3 / +0.3 / −2.0 — **reproduced within 0.4pp; his arithmetic is sound.**

`26_exfx_acceleration_v2.csv`. The kernel base is ⅔·GBV(q−1) + ⅓·GBV(q−2); its 3Q26 y/y is **+16.9%** and does not depend on the 3Q26 GBV estimate, while its 4Q26 y/y does.

| 3Q26 GBV | kernel base y/y, 4Q26 | base step | FX step (C) | **ex-FX** | sign |
|---|---|---|---|---|---|
| **$26,185M** (frozen card) | +14.8% | −2.10pp | −1.9 | **−0.19pp** | **decelerates** |
| $26,300M (architect central) | +15.2% | −1.77pp | −1.9 | +0.14pp | accelerates |
| **$26,550M** (B4 request) | +15.9% | −1.05pp | −1.9 | **+0.86pp** | **accelerates** |
| $25,900M | +14.0% | −2.93pp | −1.9 | −1.03pp | decelerates |
| $27,000M | +17.2% | +0.25pp | −1.9 | +2.15pp | accelerates |

**The sign flips, and the break-even is $26,250M** under the adopted reading C (it is $26,288M under reading A, $26,405M under C2, $26,477M under B and $26,784M under the free fit D). The frozen card sits $65M below the break-even; $26,550M sits $300M above it. **A $65M move in a $26bn GBV estimate — 0.25% — changes the sign of the sentence.** That is a weaker claim than "ex-FX accelerates +0.4pp" and it is the one the arithmetic supports.

---

## 7. What the memo may say

> **Every point of the Q4 deceleration is the dollar, carried through the kernel rather than applied to it.** Lagged-GBV growth steps from +16.9% in 3Q26 to +14.8–15.9% in 4Q26 — a deceleration of 1.1 to 2.1 points depending on where 3Q26 GBV prints — and the booking-date FX carried in that base steps from about +2.9pp to about +1.0pp, a deceleration of **1.9 points**. Set one against the other and **ex-FX growth is flat**: −0.2pp at the frozen card's $26,185M, +0.1pp at $26,300M, +0.9pp at $26,550M, with the sign turning at **$26,250M**. We will not write "ex-FX accelerates" without naming the GBV and the FX reading, because the claim is worth a quarter of a percent of GBV. What we will write is that **the Q4 guide-versus-Street question is not a demand question**: on 5 November management will guide Q4 with roughly one point of FX tailwind where they guided Q3 with three, the step is about two points, and it is arithmetic that was fixed in the currency markets of the second and third quarters. The repo's own bridge subtracts that step a second time and lands $110M low; the guide-anchored walk holds it flat and lands $45M high; the two are 6 points and $167M apart on a single line item. **We can say what management will say about FX before they say it, we can say why the two loudest internal numbers are both wrong, and we can say in advance which 3Q26 FX print on 5 November would prove us wrong** — a printed +3 vindicates the lagged kernel and management's own arithmetic, a printed 0 or +1 vindicates the free fit we registered, and we will report a +2 as ambiguous rather than as a win.

---

## 8. What failed, and what I will not claim

1. **The refresh is five business days, not fourteen.** FRED H.10 last prints 2026-09-04. Nothing here is genuinely "as of 11 September"; every spot-held number is as of 4 September, and the observed-share table carries the publication lag as a separate column rather than pretending it away.
2. **The full-sample rejection of Φ stands, and the live evidence for Φ is n = 3.** Both are reported. Neither is allowed to suppress the other, and the 5 November decision rule is written before the print.
3. **The 0.851 scale is a construction, not a fitted object.** The scale fitted to the Φ shape itself is 0.653 and is still rejected at p 0.0072. Both numbers appear in every table where either appears.
4. **The fitted scale of 0.95 (gross) against the disclosed 0.56 remains a red flag on the judgement basket weights**, whose 95% CS [0.63, 1.33] excludes 0.56. That is a finding about the weights understating exposure by ~70%, not about the lag, and it is a caveat on every basket-derived pp here.
5. **The M6 FY27 row is our reconstruction of the M6 rule, not an M6 number.** The M6 forward table stops at 2Q27. It is labelled as such in the file and in the table.
6. **H2 still covers only 10 of 14 W1 quarters** and is not quotable as a W1 winner under the survives-both-windows rule. `fx_pts_revenue` has no naive baseline in the harness at all, so no FX object survives either window on the scoreboard's own definition; the 0.99pp is an **RMSE in pp, not a ratio**.
7. **The forward curve is not derivable from FRED** and is not fabricated.
8. **No FX pp is added to revenue anywhere.** No forward hedge file is added on top of stated after-hedge FX. No FX pp is quoted to two decimals in prose.
9. **`harness/score.py` was not run**, as instructed. The two new registry files were written through the harness's own `register()`.

## 9. Files written (all new; nothing overwritten)

Code — `analysis/src/forecast_methods/fx_lag_v2/`: `fetch_fx_v2.py`, `common.py`, `baskets.py`, `panel.py`, `fits.py`, `pit_fx.py`, `stages.py`, `exhibit.py` (new module), `registry_out.py`, `run.py`, `README.md`.

Data — `data/processed/forecast_methods/fx_lag_v2/`: `fx_daily_2026-09-11.csv`, `fx_quarterly_2026-09-11.csv`, `fx_fetch_manifest_2026-09-11.csv`, `00_pit_caveats.csv`, `00_summary.json`, `01_currency_quarterly_yoy.csv`, `01b_basket_weights_used.csv`, `02_basket_quarterly.csv`, `03_basket_reconciliation.csv`, `04_analysis_panel.csv`, `06_object_a_summary.csv`, `06b_object_a_hypothesis_tests.csv`, `09b`–`09f` (PIT replays and scores), `19_baskets_spot_held_v2.csv`, `20_observed_share_triple.csv`, `21_live_3q26_three_numbers.csv`, `22_hedge_gross_vs_after.csv`, `23_forecast_4q26_v2.csv`, `23b_fy27_annualisation_v2.csv`, `24_four_way_4q26.csv`, `25_four_way_fy27.csv`, `26_exfx_acceleration_v2.csv`, `27_kernel_carried_fx_v2.csv`.

Registry — `data/processed/forecast_methods/registry/`: `fx-lag-v2__fx_pts_revenue_2026q4_v2.csv`, `fx-lag-v2__fx_rev_next_q_h2_v2.csv`.
