# N. Two decisions: the ADR-FX estimator to name, and the 4Q26 lap case to run on

- **Date:** 2026-09-11. **Author:** Krishang Surapaneni (compiled with Claude Code).
- **Workstream:** ADR v3 run, WS-N. Branch `krish/adr-v3`, worktree `C:\Users\krish\citadel-abnb-adrv3`.
- **Scripts:** `analysis/src/adrv3/N1_fx_estimator.py`, `analysis/src/adrv3/N2_q4_lap.py` (`py -3.13`, offline, seconds).
- **Outputs (`data/processed/adrv3/N/`):** `N1_fx_estimator_by_quarter.csv`, `N1_fx_estimator_window_summary.csv`, `N1_fx_estimator_reconciliation_check.csv`, `N1_fx_choice_card.csv`, `N2_q4_lap_cases.csv`.
- **Not a test.** Per the BRIEF, these are decision memos, not pre-registered pass/fail workstreams. No new data was collected; every number is a transform of files already committed by WS-B, WS-D, WS-H, WS-J and WS-S.

---

## Bottom line

1. **Memo 1: name the midpoint of the euro fit and the regional-basket build as the ADR-FX estimator.** Recomputed from WS-B's own backtest file, the midpoint beats both single estimators on the full 2Q22-2Q26 record (RMSE 0.406pp against euro 0.458 and baskets 0.535, a comparison WS-B never ran) and on WS-S's scored window 1Q24-2Q26 (0.332 against euro 0.455 and baskets 0.416). The two single estimators trade off by era (euro wins the 2022 broad-dollar surge, baskets win the 2024-26 regionally-divergent era) and 3Q26/4Q26 resemble the second era, not the first, so baskets alone would be a reasonable second choice; the midpoint is recommended because it is the best performer in both eras and its worst-case degradation, in the era where it is not the best, is small. **3Q26 reported ADR +3.03% ($176.47); 4Q26 +3.61% ($173.55), both on card v2's ex-FX base of +3.46 for both quarters.**

2. **Memo 2: adopt the WS-D global-lap case as the 4Q26 nights baseline, with the team baseline of 8.9% (132.7mm) kept as the top of the band, not the point.** WS-D's case rests on sourced dates (the 4Q25 and 3Q25 letters date the cancellation redesign and single-fee tranche 1 to October to December 2025, globally) against PR #32's undated assumption that these two features are North-America only, which the letters contradict on geography. The one free parameter, the ex-NA fee-and-cancellation share of the ex-NA bundle, is pinned at 40-50% by an out-of-sample check against the 4Q25 "over 200bps" disclosure (this is the one place in this memo where a split is assumed rather than sourced). **4Q26 nights +8.0 to +8.2% (131.7-131.9mm), point 8.1% (131.8mm) at the midpoint of the pinned split**, against the team baseline of +8.9% (132.7mm). At card v2's midpoint-FX 4Q26 ADR ($173.55), this is a revenue difference of about $21mm (4Q26 revenue $3,115mm against $3,137mm), small next to the anticipated Q4 guide range ($3,050-3,100mm) and the historical guide-to-actual cushion (about $100-120mm). The nights points move by a full point; the revenue dollars barely move, because ADR and take rate do the same work in both cases. **The single 5 November disclosure that would settle it is not the aggregate nights print or the Q4 guide number** (both cases sit inside WS-D's own pre-registered "inconclusive" band of 7.6-9.4% for the 4Q26 guide), **but whether management repeats a quantified bundle contribution for 3Q26** (as it did in 4Q25 and 1Q26, then stopped in 2Q26): a figure at or below about 1.5 points is consistent with the ex-NA anniversary already biting (Case B); a figure at or above about 2.5 points is consistent with the bundle still adding regardless of geography (Case A).

---

## Memo 1: which ADR-FX estimator to name

### 1. The apparent conflict

WS-B, on the 17 quarters of disclosed ADR FX from 2Q22 to 2Q26, reports the euro fit at RMSE 0.458pp against the regional-basket build at 0.535pp: euro wins. WS-S, scoring the same two estimators (unchanged from WS-B) against the disclosed FX effect on the walk-forward window 1Q24-2Q26 (n10), finds baskets at 0.416pp and the midpoint at 0.332pp both beating euro at 0.455pp: euro loses. Both numbers are correct; they are different windows.

### 2. Reconciliation, by quarter and by sub-window

`N1_fx_estimator_by_quarter.csv` recomputes the absolute error of all three estimators (euro, baskets, and their midpoint, which neither WS-B nor WS-S scored over the full record) for every one of the 17 disclosed quarters, and `N1_fx_estimator_window_summary.csv` aggregates by sub-window.

| Window | n | RMSE euro | RMSE baskets | RMSE midpoint | Quarters euro wins | Quarters baskets win | Quarters midpoint wins |
|---|---|---|---|---|---|---|---|
| Full, 2Q22-2Q26 | 17 | 0.458 | 0.535 | **0.406** | 7 | 6 | 4 |
| 2022 dollar surge (2Q22-4Q22) | 3 | **0.152** | 0.726 | 0.333 | 3 | 0 | 0 |
| 2023, unwind and mixed | 4 | 0.598 | 0.623 | 0.585 | 1 | 2 | 1 |
| Scored, 1Q24-2Q26 | 10 | 0.455 | 0.416 | **0.332** | 3 | 4 | 3 |
| Scored, 2Q24-2Q26 | 9 | 0.429 | 0.432 | **0.343** | 3 | 4 | 2 |

Sourced (descriptive, recomputed from `data/processed/overnight2/B/B_adr_fx_estimator_backtest.csv`, which already carries WS-B's fitted estimates and disclosed FX effect; no new fit was run).

**Where each wins and why.** The 2022 sub-window is the broad-dollar surge: EUR/USD fell to parity and the euro fit, calibrated directly on that pair, tracks it almost exactly (RMSE 0.152, wins all three quarters); the basket build, carrying non-euro currencies that moved less, misses badly (0.726). The scored 2024-26 window is not a broad-dollar move: it is regionally divergent, with the Latin American and Asia-Pacific baskets running well ahead of the euro cross (see WS-B table 2.4: LatAm basket y/y +6.7 to +12.3 across 2025-26 quarters against EMEA flat to negative), and here the euro fit is biased persistently negative (bias -0.13pp on the scored window) because it has no channel for that divergence, while baskets (bias +0.01, essentially unbiased) and the midpoint (bias -0.06) track it. 2023 is the transition year and no estimator dominates (each wins at least one quarter of four).

**The midpoint reconciles the two rankings rather than choosing between them.** Over the full 17-quarter record, the midpoint's RMSE (0.406) is lower than both single estimators, including euro on its own best turf: averaging in the worse basket estimate during the 2022 surge (0.333) still beats baskets alone (0.726) by enough to pull the blended full-window RMSE below euro's. Over the scored window, the midpoint (0.332) beats baskets (0.416), which beats euro (0.455). WS-B's and WS-S's rankings are therefore not in conflict; they are each correct within their own window, and the reason WS-B did not find the midpoint's advantage is that its note scored only the two single estimators, never their average, over the full record.

### 3. Which regime 3Q26 and 4Q26 resemble

The 3Q26/4Q26 flat-spot path (`B_fx_translation_schedule_refresh.csv`, `B_intraquarter_3q26_path.csv`) is a quiet-dollar, regionally-divergent quarter, not a broad-dollar surge: EUR/USD y/y is -1.2% in 3Q26 and -0.2% in 4Q26 (essentially flat), while the regional baskets diverge sharply, LatAm +6.7%/+6.2% and APAC +2.2%/+5.3% against EMEA -0.9%/+0.3% and NA +0.1%/+0.2%. This is structurally the same shape as the scored 2024-26 window (calm aggregate dollar, wide regional spread), not the 2022 surge (a large, EUR-dominated move with narrow regional spread). On that basis the estimator that wins in the scored window, not the one that won in 2022, is the relevant comparison for 3Q26 and 4Q26.

### 4. The 3Q26 and 4Q26 card

Card v2's ex-FX base is +3.46pp for both quarters (`data/processed/adrq3/J/adr_card_v2.csv`; card v2 carries workstream I's 3Q26 mix terms into 4Q26 for lack of a fresh 4Q26 mix read, so the ex-FX figure is identical across the two quarters, sourced from J).

| Quarter | Estimator | FX effect pp | Reported ADR y/y pp | Reported ADR $ |
|---|---|---|---|---|
| 3Q26 | euro fit | -1.12 | 2.34 | 175.29 |
| 3Q26 | baskets | +0.26 | 3.72 | 177.66 |
| 3Q26 | **midpoint (recommended)** | **-0.43** | **3.03** | **176.47** |
| 4Q26 | euro fit | -0.66 | 2.80 | 172.20 |
| 4Q26 | baskets | +0.97 | 4.43 | 174.93 |
| 4Q26 | **midpoint (recommended)** | **+0.15** | **3.61** | **173.55** |

Sourced (all four columns read from `adr_card_v2.csv` and `N1_fx_choice_card.csv`; the FX effects and ex-FX base are card v2's, unchanged here).

### 5. Recommendation and what would change it

**Recommend the midpoint of the euro fit and the regional-basket build**, not either estimator alone. It is the best performer on both the full record and the scored window (section 2), and in the one era where it is not the single best (the 2022 surge, where euro dominates), its degradation is small relative to picking baskets and being wrong. This is a complementary-estimator case in the sense the BRIEF anticipated: the two single estimators are not competing measurements of the same thing so much as two lenses that each miss a different part of the FX picture (euro misses regional divergence; baskets, whose origin and destination weights are WS-B's own judgment calls and flagged as weakest for EMEA, likely add noise of their own in a genuine broad-dollar move), and averaging them is a hedge against either failure mode.

**What would change the recommendation:**
- A return to a broad, EUR-dominated dollar move before or during 4Q26 (large EUR/USD swing with the regional baskets moving in the same direction and magnitude, unlike the current divergent pattern) would favor the euro fit alone, as in 2022.
- If the FX path drifts further before quarter-end 3Q26 in a way that breaks the flat-spot assumption underlying both estimators' point forecasts (the schedule refresh holds spot flat for the last 18 business days of 3Q26 and all of 4Q26; FOMC sits on 16 Sep and 28 Oct inside this window), the point estimates above would need refreshing regardless of which estimator is named.
- If WS-B's origin-weight judgment calls for the regional baskets (flagged in the B note as anchored on eight disclosed or third-party points, with the EMEA weight explicitly the weakest) are shown to be materially wrong, that would push the choice back toward euro alone, since the midpoint's advantage depends on the basket estimator being at least roughly right.
- The 3Q26 print itself (5 November) scores all three estimators directly against the disclosed FX effect and is the next real test; if euro turns out closer that quarter, it would be one more data point in a small sample, not by itself a reason to reverse this recommendation.

### Method

`analysis/src/adrv3/N1_fx_estimator.py` reads `data/processed/overnight2/B/B_adr_fx_estimator_backtest.csv` (WS-B's already-fitted euro and regional-basket estimates and the disclosed FX effect, 2Q22-2Q26, 17 rows) and `data/processed/adrq3/J/adr_card_v2.csv` (card v2's 3Q26/4Q26 ex-FX base and per-estimator FX effect and reported ADR). It computes the midpoint estimator as the simple mean of the euro and basket estimates (no new fit), computes RMSE and bias by quarter and by sub-window (2022 surge, 2023, scored 1Q24-2Q26, scored 2Q24-2Q26, full), and reproduces WS-B's and WS-S's published numbers exactly as a check (`N1_fx_estimator_reconciliation_check.csv`: full-window euro 0.458 and baskets 0.535 match B to three decimals; scored-window euro 0.455, baskets 0.416, midpoint 0.332 match S's `error_attribution_v3.csv` exactly). No parameter is fitted in this script; it is a pure transform and aggregation of numbers WS-B and WS-J already computed.

### What this can and cannot identify

**Can.** Show, from the same source file, why WS-B and WS-S ranked the estimators oppositely (different windows, different eras), and show that averaging the two estimators is not merely a compromise but the best performer on both windows examined here. Say which of the two historical eras 3Q26/4Q26 structurally resemble, on the observed FX path through 4 September 2026.

**Cannot.** Prove the midpoint will be the best estimator in 3Q26 or 4Q26 specifically; the reconciliation is a backtest over 14-17 quarters, not a guarantee for the next two. Distinguish whether the regional-basket build's good recent performance reflects a real, persistent structural shift (a more regionally fragmented FX environment) or is itself an artifact of WS-B's judgment-based origin weights happening to fit the last two years well. Say anything about an estimator this memo did not test (the broad-dollar fit, which WS-B and WS-H excluded on the same 17-quarter record at RMSE 0.868, well behind both estimators considered here).

### Files

| File | Contents |
|---|---|
| `analysis/src/adrv3/N1_fx_estimator.py` | reconciliation script: per-quarter and per-window RMSE and bias for euro, baskets and midpoint; reproduction check against B and S; the 3Q26/4Q26 card |
| `data/processed/adrv3/N/N1_fx_estimator_by_quarter.csv` | 17 rows, one per disclosed quarter 2Q22-2Q26: each estimator's value, error, absolute error, sub-window label, per-quarter winner |
| `data/processed/adrv3/N/N1_fx_estimator_window_summary.csv` | RMSE, bias and win counts by sub-window (full, 2022 surge, 2023, scored 1Q24-2Q26, scored 2Q24-2Q26) |
| `data/processed/adrv3/N/N1_fx_estimator_reconciliation_check.csv` | this script's recomputed RMSEs against WS-B's and WS-S's published numbers, confirming reproduction |
| `data/processed/adrv3/N/N1_fx_choice_card.csv` | 3Q26 and 4Q26, all three estimators: FX effect, ex-FX, reported ADR pp and dollars, with the scored- and full-window RMSE attached and the recommended row flagged |

---

## Memo 2: the 4Q26 lap decision

### 1. The question

PR #32 laps the RNPL, cancellation-redesign and single-fee bundle in North America only, giving a 4Q26 team baseline of +8.9% nights (132.7mm). WS-D's ledger dates the cancellation redesign and single-fee tranche 1 to October to December 2025, globally (the 4Q25 letter: "In October, we announced new cancellation policies..."; the fee migration ran PMS hosts from October, most remaining single-fee hosts from December), not North-America only. If those two legs are lapped ex-NA as well, at an ex-NA fee-and-cancellation share of the ex-NA bundle pinned at 40-50% by an out-of-sample check against the 4Q25 disclosure, the 4Q26 baseline moves to 8.0-8.2% (131.7-131.9mm).

### 2. The two cases, side by side

All inputs sourced except the one row marked assumed.

| Item | Case A: team baseline (PR #32, NA-only lap) | Case B: WS-D global lap (pinned 40-50% ex-NA split) |
|---|---|---|
| Geography of the Oct-Dec 2025 cancellation redesign and single-fee tranche 1 | assumed NA-only by PR #32's model structure | **sourced**: global, per the 3Q25 and 4Q25 shareholder letters (D012, D013, D024, D060 in `rnpl_statement_ledger.csv`) |
| Ex-NA fee-and-cancellation share of the ex-NA bundle | n/a (not modelled ex-NA) | **assumed**, pinned at 40-50% by an out-of-sample check: at 4Q25, ex-NA RNPL was zero (it launched 17 Feb 2026), so the ex-NA bundle then was the fee-and-cancellation legs alone, and PR #32's NA figure (1.35pts) plus this share of the implied ex-NA total must sum to management's disclosed "over 200bps"; 40-50% is the range consistent with that disclosure, 70-100% is not (`D1_bundle_crosscheck.csv`, `D1_exna_4q26_gap.csv`) |
| 4Q26 nights y/y | **8.9%** (sourced: reconciled team baseline) | **8.0-8.2%**, point 8.1% at the 45% midpoint of the pinned split (sourced dates plus the assumed split) |
| 4Q26 nights, mm | **132.7** | **131.7-131.9, point 131.8** |
| 4Q26 GBV, $bn, at card v2's midpoint-FX ADR ($173.55) | 23.03 | 22.86-22.89, point 22.87 |
| 4Q26 revenue, $mm, at the same-quarter-prior-year take rate (13.62%, `TAKE["4Q26"]` in J3's card v2 script) | **3,137** | **3,113-3,118, point 3,115** |
| 4Q26 revenue y/y | +12.9% | +12.1 to +12.2%, point +12.15% |
| Distance above the top of the anticipated Q4 guide range ($3,100mm, `research/notes/2026-09-10_h1-to-h2-bridge.md` section 7) | +37mm | +13 to +18mm, point +15mm |
| Distance above the bottom of the anticipated Q4 guide range ($3,050mm) | +87mm | +63 to +68mm, point +65mm |
| Distance to Street consensus ($3,200mm, `04_current_consensus.csv` vintage 4 Sep 2026) | -63mm | -87 to -82mm, point -85mm |

Sourced/computed in `data/processed/adrv3/N/N2_q4_lap_cases.csv`, which also carries the eur-fit and baskets-estimator sensitivities (4Q26 ADR $172.20 and $174.93 respectively) alongside the midpoint point estimate used above.

**The revenue distance between the two cases is small; the nights distance is not.** A full point of nights growth (8.9 against 8.1) is a $21mm revenue difference at the midpoint ADR, because ADR and the take rate do the same arithmetic in both cases and GBV moves only with the small nights gap. Both cases sit above the anticipated Q4 guide range and below Street consensus regardless of which case is right. **The lap decision is a nights-growth-rate question, not a revenue-dollar question**, and should be read that way when reconciling against the print.

### 3. The pre-registered thresholds this cross-checks against

`D1_prereg_thresholds.csv` pre-registers, for the 4Q26 nights guide issued 5 November: a guide implying **7.5% or below supports** the drag/global-lap hypothesis, **9.5% or above weakens it**, and **7.6% to 9.4% is inconclusive**. Both Case A (8.9%) and Case B (8.0-8.2%) fall inside that inconclusive band. This means the 4Q26 nights guide number itself, taken alone, is not designed to cleanly separate these two cases; it would need to print outside the range either case predicts (below 7.6% or above 9.4%) to be more than weak evidence either way.

### 4. Recommendation

**Adopt Case B (the WS-D global lap, 8.0-8.2%, point 8.1%) as the 4Q26 baseline, keeping 8.9% as the top of the band rather than the point.** The reasoning: the geography of the cancellation redesign and single-fee tranche 1 is sourced directly from the 3Q25 and 4Q25 shareholder letters as global, not North-America only; PR #32's NA-only treatment of these two features is a modelling assumption the letters contradict on that specific point. The one thing WS-D adds beyond the letters, the 40-50% split, is not a free assumption either: it is pinned by requiring PR #32's own NA parameter (1.35pts) plus the ex-NA share to reproduce management's "over 200bps" 4Q25 disclosure, an out-of-sample check PR #32 did not use when it was built. This matches the standing recommendation already on record in `docs/overnight2/SYNTHESIS.md` ("recommend adopting it as the base with 8.9 as the top of the band"), reached independently here from the same underlying files.

**The single 5 November disclosure that would settle it:** whether management repeats a quantified bundle contribution for 3Q26, and at what level. Management gave "over 200bps nights, roughly 300bps GBV" for 4Q25 and "about 3 points nights, 4 points GBV" for 1Q26, then gave no figure for 2Q26 (`rnpl_statement_ledger.csv` D014, D032; ledger note point 1). A figure at or below about 1.5 points for 3Q26 would be consistent with the anniversary already biting broadly, which is what Case B implies (the ex-NA lap starts closing from 4Q26, but the NA anniversary is already inside 3Q26); a figure at or above about 2.5 points would say the bundle is still adding regardless of geography, which favors Case A's smaller, NA-only treatment of the lap. This is preferred over the aggregate 4Q26 nights guide itself precisely because, per section 3, that guide number alone sits inside the inconclusive band for both cases and would need an extreme reading to be decisive on its own.

### Method

`analysis/src/adrv3/N2_q4_lap.py` reads `data/processed/overnight2/D/D1_exna_4q26_gap.csv` for Case B's nights figures (WS-D's own arithmetic, not re-derived here) and `data/processed/adrq3/J/adr_card_v2.csv` for the 4Q26 ADR under all three FX estimators. Case A's nights figure (132.7mm, 8.9%) is the reconciled team baseline from `research/notes/2026-09-10_nights-baseline-reconciliation.md`; the exact year-over-year percentage recomputed here from the 4Q25 base of 121.9mm is 8.86%, matching the disclosed 8.9% to within the rounding of the 4Q25 base figure itself. GBV is nights times ADR; revenue is GBV times the same-quarter-prior-year take rate (13.62% for 4Q26) exactly as J3's card v2 computes it, so the revenue figures reproduce card v2's own 4Q26 midpoint row (`revenue_musd_same_q_take` 3,137) exactly at the team baseline. The Q4 guide arithmetic figures ($3,050-3,100mm) are read from `research/notes/2026-09-10_h1-to-h2-bridge.md` section 7, itself a transform of `data/processed/h2_bridge/h2_bridge_revenue_dollars.csv` (the historical guide-to-actual cushion applied to that note's own 4Q26 revenue estimate); no new guide-cushion model is fit here.

### What this can and cannot identify

**Can.** Lay out the two cases on the same disclosed inputs and the same card v2 ADR, so the nights-rate difference and the resulting revenue-dollar difference are both visible and are shown to be of very different sizes. Identify that the 40-50% split, while assumed, is not free: it is pinned by an out-of-sample cross-check against a disclosure PR #32 did not use. Identify which single disclosure has the most power to separate the two cases, using WS-D's own pre-registered thresholds rather than inventing new ones.

**Cannot.** Prove which case is correct before 5 November. Attribute a 4Q26 nights print, whatever it is, to this specific mechanism rather than to some other driver (world cup lap timing, macro demand, the RNPL cancellation propensity itself, which WS-D's cohort scenarios show is a materially smaller effect than the level lap); the ledger note is explicit that the confounds here (product bundle, macro, event calendar) cannot be separated with the data available. Resolve the 40-50% split more tightly than WS-D already has; this memo did not re-derive that pin, only used it.

### Files

| File | Contents |
|---|---|
| `analysis/src/adrv3/N2_q4_lap.py` | builds the two cases, computes GBV, revenue and revenue y/y at all three card v2 FX estimators, and the distance to the guide-arithmetic and consensus figures |
| `data/processed/adrv3/N/N2_q4_lap_cases.csv` | 12 rows (4 case variants x 3 FX estimators): nights, ADR, GBV, revenue, revenue y/y, and distance to the guide arithmetic and consensus |
