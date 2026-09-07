# WS20 — Honest temporal validation of the reaction and alt-data results

**What this is.** The repair for audit findings **A02** (the reaction tests are not a tradable
out-of-sample test) and **A03** (window sensitivity, multiple testing and data vintage are still open
research gates). It rebuilds the event returns from a price a trader could actually get, splits the
reaction work into a pre-earnings forecast task and a post-release drift task, freezes a machine-readable
experiment specification before the 5 Nov print, and re-states the two headline reaction findings under
the executable convention.

**Files.** Scripts `analysis/src/overnight/20_executable_returns.py`, `20_temporal_validation.py`,
`20_experiment_spec.py`. Data `data/processed/overnight/20_*.csv` + `20_experiment_spec.json`
(13 outputs: 20_executable_returns, 20_prices_ohlc, 20_pre_earnings_forecasts, 20_postrelease_drift, 20_task_summary, 20_prediction_ledger, 20_perturbation_check, 20_convention_restatement, 20_frozen_q3_2026, 20_experiment_spec.json, 20_vintage_register, 20_incremental_value, 20_funds_held_windows). Built on the concurrent A01/A05 fixes to `08_altdata_backtests.py` and the
A09/A11 fixes to `16_merge_and_rerun.py`; the panel used is `16_reaction_panel.csv` (23 prints).

---

## 1. Bottom line

1. **Almost the whole day-1 "reaction function" is the overnight gap, which no one can trade on the
   released numbers.** Across 23 prints the gap (pre-release close → next open, QQQ-excess) has mean
   absolute size **6.05%** against **6.81%** for the full legacy day-1 excess return, correlation
   **0.89**, and the gap accounts for **73%** of the variance of the legacy day-1 number. Entering at
   the first executable price cuts the mean absolute day-1 move to **3.22%**.
2. **The nights-surprise → 20-day drift result does not survive the executable convention.** Legacy
   (pre-release close entry): n 19, r 0.455, R² 0.207, supplementary LOO R² **+0.156**, expanding
   walk-forward RMSE **0.958×** a zero baseline. Executable (next-session open entry): r 0.311
   (p 0.194), R² 0.097, LOO R² **−0.016**, walk-forward **1.076×** the best baseline. It fails.
3. **The 9-of-9 guide-below-Street 20-day rule does survive, at roughly half the magnitude.** Under the
   executable open entry it is still **9 of 9 negative**, but the mean goes from **−8.90%** to
   **−4.21%** (median −4.42%). Binomial p vs a coin flip 0.0020, vs ABNB's own 69.6% base rate of
   negative 20-day excess **0.0382**. The day-1 half of the rule collapses entirely: only 3 of 9 are
   negative on the executable convention, mean **+0.91%**.
4. **No pre-earnings feature forecasts the nights or revenue surprise once trailing-mean baselines are
   included.** Of 51 Task A summary rows, 4 beat every baseline, covering 2 distinct feature/target
   pairs, and **neither survives in both evaluation windows**, so neither passes the frozen decision
   rule. Every apparent winner in the first pass was an intercept shift: prediction sd is 0.14–0.33×
   the actual sd, and the models beat "zero" and "expanding mean" only because the expanding mean of a
   surprise series starting in 2021 is dragged up by the COVID-rebound surprises (+16.1%, +24.2%).
5. **New point-in-time defect found (small, A01 family):** the WS08 `pr_hotel_revpar_yoy` feature
   averages Marriott and Hilton RevPAR unconditionally, but MAR reported *after* ABNB in 2023Q3 (−1 day)
   and 2025Q1 (−5 days), and HLT in 2024Q2 (−1 day). See §8.
6. **The frozen 5 Nov prediction is a baseline, not a model** (§7), because nothing beat the baselines.

---

## 2. The executable-entry convention (A02, defect 2)

`20_executable_returns.py` rebuilds every print's event return from yfinance unadjusted OHLC for ABNB
and QQQ (ABNB pays no dividend and has not split, so open-to-close arithmetic is exact). ABNB releases
after the US close on the print date, so the reaction session is the next trading day.

| Convention | Entry | Executable? |
|---|---|---|
| `legacy_*` | close of the **print date** | **No.** This is the price before the release. |
| `open_*` | **open of the reaction session** | Yes — the first printed price after the release. **Primary.** |
| `postclose_*` | close of the reaction session | Yes, but forgoes the whole day-1 move. |

`h` counts trading sessions with the reaction session as session 1, so `open_20d_pct` runs from the
reaction-session open to the close of the 20th session. All returns are ABNB minus QQQ over identical
dates. Output: `20_executable_returns.csv` (23 rows, with entry/exit dates and prices).

The size of the correction, per print, is in `gap_excess_pct`. Examples: 2023Q1 legacy day-1 −12.01%
vs executable +2.73% (gap −14.32%); 2024Q2 legacy −12.30% vs executable +3.13%; 2024Q4 legacy +14.03%
vs executable +1.65%. The legacy series is very close to a measure of the gap.

## 3. Task A — pre-earnings forecast (A02 item 1a)

**Decision time:** the close of the print date. Nothing released that evening is used.
**Targets:** `nights_surprise_pct` (n 19 available) and `revenue_surprise_pct` (n 23).
**Fits:** expanding-window OLS, chronological, **initial training 8**, one feature at a time, from a
candidate set of 8 frozen in `20_experiment_spec.json` before any of this was run.
**Baselines scored on identical events:** zero (the consensus itself), last quarter, prior year,
expanding AR(1), expanding mean, **trailing-4 mean, trailing-8 mean**, and for revenue only the **guide**
(guide midpoint vs Street set at the prior print) and **guide + trailing cushion**.

Per-event rows: `20_pre_earnings_forecasts.csv` (169). Summary: `20_task_summary.csv` (51 Task A rows =
17 model/target pairs × 3 windows).

Selected results, 2024Q1+ window (RMSE in percentage points of the surprise):

| Target | Feature | n | model | zero | trail-4 | AR(1) | guide | guide+cushion | pred sd / actual sd |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|
| revenue surprise | `f_guide_vs_street_lag1` | 10 | 1.213 | 1.899 | **1.332** | 1.736 | 2.367 | 2.026 | 0.14 |
| revenue surprise | `bl_funds_yoy_lag1` | 10 | 1.225 | 1.899 | **1.332** | 1.736 | 2.367 | 2.026 | 0.21 |
| revenue surprise | `f_surprise_trail4` | 10 | 1.285 | 1.899 | **1.332** | 1.736 | 2.367 | 2.026 | 0.18 |
| revenue surprise | `pr_hotel_revpar_yoy_pit` | 10 | 3.164 | 1.899 | 1.332 | 1.736 | 2.367 | 2.026 | 0.67 |
| nights surprise | `eu_platform_yoy_lag1` | 9 | 1.199 | 1.696 | 1.222 | 1.581 | – | – | 0.18 |
| nights surprise | `ia_reviews_ltm_matched_yoy` | – | not evaluable at min-train 8 in this window | | | | | | |

Read that table carefully. The three "good" revenue rows sit within 0.1 pp of the trailing-4 baseline,
and their prediction sd is a fifth of the actual sd — they are all forecasting "a small positive beat of
about +1.4%", which is correct and which the trailing-4 mean says for free. **`prior_year` is the best
baseline for the nights surprise (RMSE 0.99–1.01) and beats every fitted model.**

Formally: **4 of 51 Task A rows beat every baseline**, covering 2 pairs —
`eu_platform_yoy_lag1 → nights_surprise` (n 11, 2023Q3–2026Q2, ratio 0.850 vs prior year) and
`f_surprise_trail4 → revenue_surprise` (n 13, ratio 0.977 vs trailing-4, i.e. a tie with itself).
**Neither survives in the 2024Q1+ window** (Eurostat goes to 1.209), so under the frozen decision rule —
beat every allowed baseline on identical events in *both* windows — **nothing survives Task A**.

The **guide and guide+cushion baselines are the worst on this target** (RMSE 2.0–2.4 vs 1.33 for the
trailing-4 mean). That is not a contradiction of the WS02/WS16 finding that the guide plus its cushion
forecasts *revenue*; it says the guide-vs-Street gap does not forecast the *surprise vs Street*.

## 4. Task B — post-release drift (A02 item 1b)

Feature = the **actual released surprise**. Entry = the open of the reaction session. Targets
`open_5d_pct` and `open_20d_pct`; the same tests are re-run on `legacy_*` and `postclose_*` purely for
comparison and are flagged `primary_spec = False`. Expanding OLS, initial training 8.

Per-event rows: `20_postrelease_drift.csv` (222). Summary: 54 rows, of which **18 are primary**.

**Zero of the 18 primary rows beat their baselines.** All executable ratios are 1.03–1.23.

| Feature | Target | Entry | n | model RMSE | zero | ratio vs best | supp. LOO R² |
|---|---|---|--:|--:|--:|--:|--:|
| nights surprise | 20d | legacy (not executable) | 11 | 8.936 | 9.330 | **0.958** | **+0.156** |
| nights surprise | 20d | open (executable) | 11 | 7.303 | 6.785 | 1.076 | −0.016 |
| nights surprise | 20d | post-print close | 11 | 7.086 | 5.953 | 1.190 | +0.093 |
| nights surprise | 5d | open | 11 | 5.804 | 5.154 | 1.126 | −0.060 |
| revenue surprise | 20d | open | 15 | 6.889 | 6.690 | 1.030 | −0.192 |
| guide vs Street | 20d | open | 11 | 8.160 | 6.656 | 1.226 | +0.024 |

**LOO is reported only as the last column and only as description.** The audit is right that LOO is not
a trading simulation; here the two disagree in exactly the way that matters — LOO says +0.156 on the
legacy convention, the chronological executable test says the relationship is not there.

## 5. Prediction ledger, perturbation check (A02 items 3 and 4)

`20_prediction_ledger.csv` — **391 rows**, one per stored forecast. Columns: task, print quarter, target,
model, **decision time** (with the cutoff convention spelled out), **last training label quarter and the
date it became known**, n_train, feature value, forecast, actual, error, **consensus vintage** (revenue
and nights separately, with the publisher, the vendor, and a `consensus_point_in_time` flag), **entry
convention, entry time, entry price**, **return endpoint date and exit price**, and every baseline.

`20_perturbation_check.csv` — **4 checks, all pass.** For each of two cut quarters (2024Q4, 2025Q2)
every feature and every label in quarters after the cut is multiplied by −3 and given N(0,50) noise, both
tasks are re-run, and predictions dated on or before the cut are compared. Max absolute difference
**0.0** in all four checks; the script `assert`s this, so it exits non-zero on any leak (A13-friendly).

## 6. A03 — the frozen specification, vintage, and incremental value

**`20_experiment_spec.json`** (`spec_id` ABNB-WS20-v1, frozen 2026-09-06). Carries: 8 primary candidate
features with their transformations and availability, 4 primary targets with horizons and the baselines
allowed for each, equal weights / single-feature OLS with no in-loop selection, min training 8, listwise
missing-data policy (no imputation, no forward fill), the two evaluation windows, the executable entry
convention, the decision rule, an explicit multiple-testing note, and a **pointer to the separate
exploratory ledger** (`08_feature_tests_all.csv` 598 rows, `08_index_backtests.csv`,
`04_reaction_tests.csv`, `16_reaction_tests.csv`, `09_test_ledger.csv`) whose status is set to
EXPLORATORY.

**`20_vintage_register.csv`** — 13 series. Reconstructible: ABNB reported KPIs (the print date *is* the
release), print-day Street consensus (21 of 23 prints; 2 rely on a Zacks page retrieved 2026-09-04 and
are supplementary), guide midpoints, peer report dates, Inside Airbnb dump dates, Common Crawl crawl
dates, prices. **Not reconstructible, conservatively lagged and labelled APPROXIMATION:** Eurostat
platform nights (revised, current vintage only — the one-quarter lag is the control), XBRL funds
held/unearned fees (companyfacts returns currently-reported values, no restatement vintage), FRED macro
and BEA hotel series (current vintage; ALFRED not used). **Excluded from the primary set entirely:**
Google Trends, because Google renormalises the whole history on every pull, so today's history is not
the history a 2023 decision-maker saw.

**`20_incremental_value.csv`** — 77 tests: baseline vs baseline + feature on **identical events**, both
windows. Baseline = expanding AR(1); the feature model adds the feature to that same AR(1). A feature
counts only if it beats AR(1), naive last quarter, prior year and the trailing-4 mean. **14 of 77 add
value.** The robust ones are hotel RevPAR into nights growth (ratio 0.551 raw / **0.576 after the
point-in-time correction**, n 9) and into revenue growth (0.885 / 0.900). On the surprise targets only
2 add value and both only in 2023Q1+.

**`20_funds_held_windows.csv`** — the funds-held case in both windows side by side, with the
training-start effect separated from the evaluation-window effect, and the original WS08 rows carried in
the same file so the two can never be quoted across files:

| Method | Target | Train from | Evaluate | n | ratio vs naive | ratio vs AR(1) |
|---|---|---|---|--:|--:|--:|
| WS08 single feature (min-train 4) | rev_yoy | 2022Q1 | 2023Q1+ | **14** | **1.691** | **1.846** |
| WS08 single feature (min-train 4) | rev_yoy | 2023Q1 | 2024Q1+ | **10** | **0.600** | **0.590** |
| WS20 AR(1)+feature (min-train 8) | rev_yoy | 2022Q1 | 2023Q1+ | 9 | 0.928 | 1.027 |
| WS20 AR(1)+feature (min-train 8) | rev_yoy | 2023Q1 | 2024Q1+ | 5 | 0.710 | 0.716 |
| WS20 AR(1)+feature | nights_yoy | 2023Q1 | 2024Q1+ | 5 | 1.069 | 0.814 |
| WS20 AR(1)+feature | gbv_yoy | 2023Q1 | 2024Q1+ | 5 | 1.429 | 1.369 |

Every row carries its own n. **n = 14 goes with 1.69/1.85 and n = 10 goes with 0.60/0.59; they are
different samples and different training histories.** The favourable number also depends on dropping the
2022 training quarters, not only on the later evaluation events.

## 7. The frozen 5 Nov 2026 prediction rows

`20_frozen_q3_2026.csv` — 18 rows. 16 are the primary features fitted on labels through 2026Q2; two
(`pr_hotel_revpar_yoy_pit`, `eu_platform_yoy_lag1`) are marked **PENDING at 2026-09-06** because MAR/HLT
report 3Q26 in late October and Eurostat 2Q26 is not yet in the pull. Because nothing beat the baselines
in both windows, the **designated** forecast is the surviving baseline:

| Target | Designated forecast | 1-sd band | Street bar used | Implied print |
|---|--:|---|---|---|
| **Revenue surprise vs Street** | **+1.37%** (trailing-4 mean) | +0.46 to +2.29 pp | $4,740m (Zacks, 7 est., 4-Sep-26) | **$4,805m** |
| **Nights surprise vs Street** | **+1.83%** (trailing-4 mean) | +0.62 to +3.03 pp | ~145m (implied bar, `04_q3_2026_breakeven.csv`) | **~147.6m** |

The feature rows are recorded so their prospective errors can be scored against that baseline on
5 November. The feature model spread is narrow and mostly below the baseline: revenue-surprise forecasts
run +1.42% to +1.81% (`bl_funds_yoy_lag1` +1.48, `f_guide_vs_street_lag1` +1.81, `f_guide_cushion_trail4`
+1.79, `f_surprise_trail4` +1.42, `ia_reviews_ltm_matched_yoy` +1.64, `f_prior_surprise` +1.60);
nights-surprise forecasts run +0.35% to +1.20%, i.e. every feature is *below* the baseline on nights.

**Vintage caveat on the frozen row.** The revenue feature `f_guide_vs_street_lag1` = **+2.603%** is the
6-Aug-26 vintage (LSEG next-quarter $4,610m vs the $4,730m guide midpoint). The current Zacks $4,740m is
a *later* vintage and is deliberately not the feature. The realised target will be measured against the
print-day consensus on 5 Nov, which is not yet known; if that consensus differs from $4,740m the implied
print level changes but the surprise forecast does not.

**Do not change `spec_id` ABNB-WS20-v1 before 5 November.** Any change to the feature set,
transformations, windows or baselines makes the 5 Nov observation exploratory rather than prospective.

## 8. Corrections to existing work

1. **`analysis/src/overnight/08_altdata_backtests.py`, `peer_features()`** — `pr_hotel_revpar_yoy` is
   `mean(mar_revpar_yoy, hlt_revpar_yoy)` for the quarter, with no check on whether the peer had
   reported. `02_peer_prints.csv` shows MAR reported **after** ABNB in 2023Q3 (lead −1 day) and 2025Q1
   (−5 days), and HLT in 2024Q2 (−1 day). The feature is therefore not point-in-time at 3 of 23 prints,
   although it is labelled "available before print" in `08_feature_tests_all.csv`. WS20 uses
   `pr_hotel_revpar_yoy_pit`, which averages only peers with `lead_days > 0`. The effect is small:
   hotel RevPAR → nights growth incremental ratio moves 0.551 → 0.576. **Not edited; recorded here.**
2. **`research/notes/overnight/04_consensus-and-reaction.md` line 243 and the WS16 update** quote the
   guide-below-Street base-rate p as 0.078 and 0.057 respectively. On the current panel, with 2026Q2's
   20-day return now available, ABNB's unconditional negative-20-day base rate is **0.696 on n 23**
   (not 0.727 on n 22), and the base-rate p is **0.0382**. The finding gets slightly stronger, not
   weaker; the number should be restated with its n.
3. `f_guide_vs_street_lag1` for 2021Q3 is direction-only (Reuters), magnitude unknown; it is coded as
   `guide_below_street = 1` for the sign test, as WS04 does, but it is missing from every regression.

## 9. Test count and what survives

| Family | Tests run | Survive the honest protocol |
|---|--:|--:|
| Task A summary rows (17 pairs × 3 windows) | 51 | 4 rows / 2 pairs beat every baseline; **0 in both windows** |
| Task B summary rows (18 pairs × 3 windows) | 54 | **0 of the 18 primary (executable) rows**; 4 rows survive only on the non-executable legacy/post-close conventions, all at ratio 0.96–0.98 |
| Convention restatement rows | 13 | 1 (guide-below-Street 20-day, both executable conventions) |
| Incremental value (baseline vs baseline+feature) | 77 | 14, concentrated in hotel RevPAR → nights/revenue growth |
| **Total** | **195** | **≈2 findings** |
| Per-event predictions stored | 391 | — |
| Leakage perturbation checks | 4 | 4 pass |

**Survives:** (i) the guide-below-Street 20-day risk flag, 9/9 negative, mean −4.21% under executable
entry, base-rate p 0.0382; (ii) hotel RevPAR as an incremental input to *nights growth* (not to the
surprise vs Street), which also survives the point-in-time correction.
**Does not survive:** the nights-surprise 20-day drift under any executable entry; every pre-earnings
alt-data forecast of the nights or revenue surprise; the funds-held signal in the earlier window.

## 10. A03 item 4 — sentences to reword (do not edit; a later agent applies these)

The WS08 guide reconciliation is **consistency evidence**, not a beat forecast: it shows that nights +11%,
an independently estimated ADR +4.05% and a chosen zero revenue-minus-GBV gap reproduce the guide
midpoint. Choosing the gap is what makes it land, so it demonstrates the guide is internally coherent,
not that ABNB will beat.

| File | Line | Current text (abridged) | Suggested change |
|---|--:|---|---|
| `08_altdata-index-and-backtests.md` | 225 | "The guide midpoint is reproduced exactly by nights +11%, ADR +4.05% and a zero revenue-minus-GBV gap." | Prefix with "**Consistency check, not a forecast:**" and add "the gap is a chosen input, not an estimate, so this shows the guide is internally coherent — it is not evidence about whether ABNB beats it." |
| `08_altdata-index-and-backtests.md` | 273 | "Do not say the guide looks conservative or aggressive on demand. The guide midpoint is exactly reproduced by…" | Keep, but append "This is a reconciliation, not a beat forecast. WS20 finds no pre-earnings feature that forecasts the revenue surprise vs Street better than a trailing-4-quarter mean." |
| `08_altdata-index-and-backtests.md` | 28 | "…add that back and it lands on the guide." (finding 6) | Add "Landing on the guide after an adjustment chosen to make it land is consistency, not validation." |
| `14_master-synthesis.md` | 106 | "Nights vs the **StreetAccount nights consensus** drives the 20-day drift … LOO R² +0.13 … The best out-of-sample reaction result in the run" | Replace the verdict: the 20-day window in that row starts at the **pre-release close**. On an executable next-open entry, LOO R² is **−0.016** and the expanding walk-forward is **1.076×** the zero baseline (`20_task_summary.csv`, `20_convention_restatement.csv`). Restate as "does not survive an executable entry convention." |
| `14_master-synthesis.md` | 551 | "**Nights vs Street nights → 20-day drift** … Not yet. 18 observations …" | Same substitution; the reason for "not yet" is now the entry convention, not only n. |
| `14_master-synthesis.md` | 262, 554, 585, 615, 751 | "9 of 9 negative, base-rate p 0.057", "mean −8.90%" | Add the executable restatement: still **9/9**, but mean **−4.21%** on a next-open entry, base-rate p **0.0382** on n 23. Say which convention each magnitude belongs to. |
| `docs/overnight/FINAL_SUMMARY.md` | 40–41 | "**Nights versus the Street's nights number** predicts the 20-day drift (the only reaction result that survives out of sample)." | Delete or replace: it survives only on a pre-release-close entry that cannot be transacted. Replace with "No reaction result survives once the return starts at the first executable price." |
| `docs/overnight/FINAL_SUMMARY.md` | 67 | "All eight prints where the guide came in below Street had a negative 20-day return." | "All **nine**… and it survives an executable next-open entry at mean −4.21% (base-rate p 0.038, n 23)." |
| `docs/overnight/FINAL_SUMMARY.md` | 33 | "**The guide plus its trailing cushion forecasts revenue** with a 1.1% mean error." | Keep, but scope it: it forecasts the revenue **level**. It is the *worst* baseline for the revenue surprise **vs Street** (RMSE 2.03 vs 1.33 for a trailing-4 mean, n 10). |

## 11. For the model

| Parameter | Value | Unit | Source |
|---|--:|---|---|
| Q3-26 revenue surprise vs Street (designated) | +1.37 | % | `20_frozen_q3_2026.csv` |
| Q3-26 nights surprise vs Street (designated) | +1.83 | % | `20_frozen_q3_2026.csv` |
| Guide-below-Street 20-day excess, executable entry | −4.21 | % mean, 9/9 | `20_convention_restatement.csv` |
| Day-1 excess return actually capturable (mean abs) | 3.22 | % | `20_executable_returns.csv` |
| Share of legacy day-1 variance that is the overnight gap | 73 | % | `20_executable_returns.csv` |

## 12. For the 5 Nov card

- The frozen forecast is **+1.4% revenue surprise (≈$4,805m) and +1.8% nights surprise (≈147.6m)**, from
  a trailing-4-quarter baseline. If the print lands inside the 1-sd bands, that is a pass for the
  baseline and tells you nothing about the alt data.
- **Do not size a trade on a day-1 reaction model.** Three quarters of the historical day-1 signal is an
  overnight gap you cannot enter.
- The one usable rule remains the binary risk flag: if the Q4 guide midpoint comes in below the
  then-current Street revenue number, the 20-day executable excess return has been negative 9 of 9 times,
  mean −4.21%. Use it for sizing, not as a short.
- Score the 16 feature rows in `20_frozen_q3_2026.csv` against the two baseline rows on 6 November,
  before touching the spec. That is the first genuinely prospective observation the study will own.

## 13. What to build next

1. Repeat the exercise for the guidance target (next-quarter guide midpoint vs then-current Street),
   which WS20 did not cover.
2. Reconstruct one true vintage series — Eurostat via its own revision archive, or FRED via ALFRED — and
   re-run the two Eurostat/macro results to see whether the current-vintage approximation flatters them.
3. Capture the print-day consensus for 5 Nov *before* the release, timestamped, so the 2026Q3 row of the
   ledger is point-in-time by construction rather than by reconstruction.
4. Widen Task B to a proper event-time panel (open-to-open horizons, and a volatility-scaled target), and
   check whether the guide-below-Street flag is anything more than a beta/momentum artefact.
