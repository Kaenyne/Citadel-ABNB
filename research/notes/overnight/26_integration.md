# 26. Integrating the audit repairs (workstreams 19-25) into the model, the synthesis and the summary

*Overnight run follow-up, 7 September 2026. Working tree `C:\Users\krish\citadel-abnb-overnight`,
branch `krish/overnight-synthesis`. Inputs: `research/notes/overnight/19_audit-triage-and-repairs.md`
through `25_conventions-and-cleanup.md`, `docs/overnight/RUN_STATE.md`, and the independent audit
handoff those notes triage. Nothing was committed.*

**Deliverables.** `analysis/src/overnight/26_change_ledger.py` ->
`data/processed/overnight/26_change_ledger.csv` (**70 rows**, every number this pass moved *and* eight
rows recording where a plausible knock-on turned out to be exactly zero). Code changes in
`analysis/src/abnb_exsbc_stack.py`, `analysis/src/overnight/{08_altdata_backtests, 09_stock_behaviour,
11_competition_supply_overlays, 13_driver_model, 13_excel_builder, 15_claim_checks, 15_script_runs,
17_scenario_switch, 23_update_ws09_options}.py`. Prose changes in `model/assumptions.md`,
`docs/overnight/FINAL_SUMMARY.md` and `research/notes/overnight/{08,11,13,14,15}_*.md`.

---

## 1. Bottom line

**Three headline prices moved and one did not.** The football-field means fall — base **$160.22 ->
$156.79**, bear **$75.95 -> $74.18**, bull **$232.68 -> $228.18** — entirely because the FY2028E
EV/EBITDA lens is now discounted one year to the common ~30 Sep 2027 target date instead of being
averaged in a year late. The base football-field *high* falls hardest, **$217.51 -> $196.92**, because
that lens *was* the high. **The base EV/adj.-EBITDA FY2027E lens — the number a reader is most likely
to quote — is unchanged at $180.88**, as is the DCF at $182.59 and the reverse DCF at 7.50% / 13.32%
implied ten-year FCF growth. The 25/50/25-weighted mean-of-means goes **$157 -> $154**.

**Two data repairs landed with almost no numerical consequence, which is the honest result.** The 4Q23
ex-SBC cost-stack column fix closes a $36M identity gap and moves four 4Q23 cost lines, but it moves
**no driver-model output at all** — verified by re-running the model on the corrected inputs with the
pre-fix regulatory assumption and getting byte-identical annual and quarterly files. The regulatory
Monte Carlo repair moves the FY2028 EMEA drag input from 1.00pp to 0.96pp, worth **+$3.5M on FY2028E
base revenue (+0.02%)** and nothing at all in FY2026 or FY2027.

**What actually changed is what may be said.** The nights-surprise 20-day drift — presented until now
as the run's one out-of-sample reaction result — does not survive an entry a trader could transact.
The options "no event premium" headline is withdrawn outright. The seven-city Inside Airbnb retention
fall is half the size once Austin's scope step is removed. The alt-data guide reconciliation is
consistency evidence, not a beat forecast.

**Verification after everything.** `model/ABNB_driver_model.xlsx` rebuilt and re-dumped in real
Excel 16.0: **0 error cells in 5,553**, **216/216** named outputs and **2,353/2,353** formula cells
reconciling to the Python mirror, **144 scenario comparisons / 0 mismatches**. `17_excel_audit.py` and
`17_scenario_switch.py` both exit **0**.

---

## 2. Step 1 — the 4Q23 ex-SBC cost stack (WS25 section 5c)

`analysis/src/abnb_exsbc_stack.py` reads SBC by function out of the shareholder letter's footnote and
picked the **column** whose total was nearest a target taken from XBRL. For a Q4 the XBRL target is
FY-less-9M, and for 4Q23 that target is $270M. The 4Q23 letter's footnote has four columns — 3M Dec
2022 $254M, 3M Dec 2023 $290M, FY2022 $930M, FY2023 $1,120M — and because |254 − 270| < |290 − 270| the
parser took the **prior-year** column.

**The fix.** A new `header_years()` reads the run of four-digit year tokens immediately before the
first function row ("Operations and support"), and column selection is now restricted to the columns
whose header year equals the quarter's own calendar year before nearest-total is applied. Nearest-total
across all columns remains the fallback when the header cannot be read. This is deliberately narrow: it
also gets the right answer for 4Q22 (candidates 254 / 930), 2Q26 (897 / 487, where the letter's
column order and header order disagree in the extracted text) and every two-column Q1 letter.

**Result: 4Q23 is the only quarter that changed, and its identity gap closes exactly.**

| 4Q23 line ($M) | before | after |
|---|--:|--:|
| SBC by function, ops / pd / sm / ga (total) | 16 / 150 / 36 / 52 (254) | **17 / 179 / 33 / 61 (290)** |
| Operations & support, cash | 255.0 | **254.0** |
| Product development, cash | 282.0 | **253.0** |
| Sales & marketing, cash | 388.0 | **391.0** |
| G&A, cash | 1,151.0 | **1,142.0** |
| Adjusted EBITDA implied by the stack | 702.0 | **738.0** |
| `identity_gap` | **−36.0** | **0.0** |

`2,218 − (2,714 − 290) + 16 + 928 = 738`, the reported Adjusted EBITDA, exactly as WS25 predicted.
Cash cost as % of revenue moves pd 12.7 -> 11.4 and ga 51.9 -> 51.5; cash cost per night pd
$2.85 -> $2.56 and ga $11.65 -> $11.56. Every other quarter is byte-identical; 1Q23-2Q26 identity gaps
stay exactly zero and the rest stay within ±$1.7M.

**Every consumer re-run.** `abnb_margin_bridge.py`, `07_cost_lines_per_night.py`,
`07_margin_lever_model.py`, `02_kpi_panel.py`, then `13_driver_model.py`.

| Consumer | Outcome |
|---|---|
| `abnb_margin_bridge.csv` | FY2023->FY2025 bridge: product development **−0.68 -> −0.97** pts, G&A **+9.15 -> +9.06**, S&M −3.71 -> −3.68, ops +0.79 -> +0.78, **residual −0.36 -> 0.00** |
| `07_cost_lines_per_night.csv` | 4Q23 brand+performance marketing **$2,460M / 24.90% -> $2,424M / 24.53%**; 4Q23 and (through a y/y comparison) 4Q24 growth cells move |
| `02_kpi_panel_quarterly.csv` | the 4Q23 row's ex-SBC cost columns only; `adj_ebitda_margin_pct` unchanged at 33.3 |
| `07_margin_levers_fy26_fy28.csv` | **byte-identical** |
| `13_driver_model.py` (reads 02 and 07) | **byte-identical** annual and quarterly outputs. Isolated by holding `REG_DRAG_PP` at its pre-fix value and re-running: the cost-stack fix alone moves no model output, because the model's FY2025 cost base and its 2023-2025 seasonal margin spreads do not depend on the 4Q23 ex-SBC split |

All 17 rows are in `26_change_ledger.csv` with ids `C01`-`C17`.

## 3. Step 2 — model inputs

### 3.1 WS22's regulatory input (audit A06)

`13_driver_model.py` `REG_DRAG_PP[2028]["emea"]` **1.00 -> 0.96pp**, with the comment corrected to
"EMEA 0.36 / 1.07 / **2.03**%". `13_excel_builder.py` reads `DM.REG_DRAG_PP` directly, so only its
source string needed updating (it now names the WS22 repair and the cumulative figures).
`model/assumptions.md`'s driver row moves to `0.03/0.36, 0.05/0.71, 0.07/0.96 pp` with the reason.

Effect, base case: FY2028E revenue **$17,943.6M -> $17,947.1M** (+0.02%), adj. EBITDA
**$6,701.2M -> $6,703.9M** (margin 37.346% -> 37.353%), FCF per share **$11.0363 -> $11.0407**,
SBC-adjusted FCF per share $7.2566 -> $7.2610. Bear FY2028E revenue $14,967.6M -> $14,970.7M. **Bull
FY2028 does not move** (its regulatory-drag multiplier is zero), and **no FY2026 or FY2027 figure moves
in any scenario.**

### 3.2 The FY2028E lens (audit A12; WS25 finding, orchestrator's decision)

WS25 established that five football-field lenses value the company at end-FY2027 and the sixth
(EV / adj. EBITDA on FY2028E) at end-FY2028, undiscounted, and quantified the cost of the date mix at
**$11.46 of the base mean** ($160.22 with it, $148.76 without). **Decision applied here: discount the
FY2028E lens one year at the scenario's cost of equity** (10.5% base, from `Inputs`), so all six lenses
sit at the adopted ~30 Sep 2027 target date. **The undiscounted value is kept**, labelled, as a
sensitivity row on the `Valuation` sheet ("Sensitivity (not in the football field): EV / adj. EBITDA,
FY2028E, UNDISCOUNTED (value as of end-FY2028)") and as a lens row in `13_valuation_summary.csv`
(`EV / adj. EBITDA, FY28E (undiscounted, value at end-FY2028; sensitivity)`), excluded from the low,
high and mean. Documented in `model/assumptions.md` section "Model conventions, decided 7 Sep 2026",
decision 1.

**Old vs new, per scenario ($/share, from `13_valuation_summary.csv`):**

| | Bear before | Bear after | Base before | Base after | Bull before | Bull after |
|---|--:|--:|--:|--:|--:|--:|
| EV / adj. EBITDA, FY27E | 108.46 | **108.46** | 180.88 | **180.88** | 234.16 | **234.16** |
| EV / FCF, FY27E | 83.55 | 83.55 | 152.50 | 152.50 | 217.94 | 217.94 |
| P / SBC-adjusted FCF, FY27E | 37.23 | 37.23 | 117.26 | 117.26 | 197.40 | 197.40 |
| P / earnings proxy, FY27E | 45.34 | 45.34 | 110.58 | 110.58 | 176.49 | 176.49 |
| **EV / adj. EBITDA, FY28E** | 103.59 | **92.95** | 217.51 | **196.92** | 289.09 | **262.10** |
| DCF on FCF | 77.54 | 77.54 | 182.59 | 182.59 | 281.01 | 281.01 |
| *Sensitivity: FY28E undiscounted* | – | *103.64* | – | *217.59* | – | *289.09* |
| **Football field low** | 37.23 | **37.23** | 110.58 | **110.58** | 176.49 | **176.49** |
| **Football field mean** | **75.95** | **74.18** | **160.22** | **156.79** | **232.68** | **228.18** |
| **Football field high** | 108.46 | **108.46** | 217.51 | **196.92** | 289.09 | **281.01** |
| 12-month return vs $181.94, mean | −58.26% | **−59.23%** | −11.94% | **−13.83%** | +27.89% | **+25.42%** |

The bear high is unchanged because the FY2028E lens was never the bear maximum; the bull high becomes
the DCF lens. The two FY2028E "before" figures for bear and base also carry the +4bp regulatory change
from §3.1, which is why the undiscounted sensitivity reads 103.64 / 217.59 rather than 103.59 / 217.51.

### 3.3 Verification

| Check | Before | After | Status |
|---|--:|--:|---|
| Cells dumped from real Excel 16.0 / error cells | 5,547 / 0 | **5,553 / 0** | +6 cells = the labelled sensitivity row |
| Named outputs reconciling Excel <-> Python | 216 / 216 | **216 / 216** | `17_excel_audit.py` **exit 0** |
| Formula cells reconciling Excel <-> evaluator | 2,349 / 2,349 | **2,353 / 2,353** | +4 formulas (3 scenarios + the Active CHOOSE cell) |
| Scenario comparisons / mismatches | 141 / 0 | **144 / 0** | `17_scenario_switch.py` **exit 0** |
| Informational static-scan hits | 343 | 344 | +1 literal exponent; not a defect |

**One audit script had to be repaired to keep this honest.** `17_scenario_switch.py` hard-coded the
`Valuation` sheet row addresses of the six lenses and the three football-field statistics (`E19`…`E45`).
Inserting the sensitivity row shifted four of them by one, and the check reported **12 spurious
mismatches** while still exiting 0 on the first run. The row addresses are now resolved from
`13_reconciliation.csv`'s own `cell_reference` column, which `13_excel_builder.py` writes, so a layout
change on `Valuation` can no longer silently break the check. After the repair: 144 comparisons, 0
mismatches, exit 0.

## 4. Step 3 — WS08 downstream (WS20 section 8, WS21 section 7, WS24 paths)

Three changes to `analysis/src/overnight/08_altdata_backtests.py`.

1. **`pr_hotel_revpar_yoy` is now point-in-time.** It averaged Marriott and Hilton RevPAR
   unconditionally, but `predictive/02_peer_prints.csv` shows MAR reported **after** ABNB in 2023Q3
   (lead −1 day) and 2025Q1 (−5 days) and HLT in 2024Q2 (−1 day) — 3 of 23 prints where the feature was
   not knowable, while `08_feature_tests_all.csv` labelled it "available before print". It now averages
   only peers with `lead_days > 0`, and the panel carries
   `pr_hotel_peers_reported_before_print` as provenance.
2. **`ia_lfl_price_yoy` uses `price_pair_eligible` and the point-in-time flag.** The old filter was
   `price_comparable` alone: right about the 2026 fee-inclusive price basis, silent about partial
   scrapes. It now requires `price_pair_eligible` (price basis **and** `pair_eligible` **and** ≥500
   matched priced entire homes) **and** `pair_eligible_pit`, and reads `lfl_price_chg_median_clean`.
   The PIT flag matters because this file is a walk-forward backtest: the retrospective coverage flag
   uses *later* scrapes, so a frozen replay may only use the trailing-window judgement.
3. **The last absolute path is gone.** The FRED cache pointed at one user's session scratchpad, so on
   any other machine the whole macro family emptied without an error. It is now `<root>/data/cache/08`
   (gitignored, `ABNB_SCRATCH` overridable) and a missing series is **fetched** from FRED's keyless CSV
   endpoint rather than skipped, with a warning if the fetch fails.

**Changed test counts and results.** 598 tests before, **598 after**; **8 of the 598 rows moved**, all
of them the two repaired features, and **none crossed a threshold**. Family totals are unchanged: 29
beat naive, 7 by 20% or more, 151 flagged, 468 evaluable walk-forward.

| Test | before | after |
|---|---|---|
| `pr_hotel_revpar_yoy -> nights_yoy`, 2022Q1+ | n 18, r +0.941, WF 0.836x naive, 0.605x AR(1), sign 10/14 | **n 17, r +0.921, WF 0.943x naive, 0.698x AR(1), sign 8/13** |
| `pr_hotel_revpar_yoy -> nights_yoy`, 2023Q1+ | n 14, r +0.879, WF 0.676x naive, 0.642x AR(1) | **n 14, r +0.869, WF 0.702x naive, 0.666x AR(1)** |
| `pr_hotel_revpar_yoy -> adr_yoy`, 2022Q1+ | n 18, r −0.017, WF 1.414x naive | **n 17, r −0.287, WF 1.306x naive** |
| `ia_lfl_price_yoy -> adr_yoy`, both windows | n 8, r **+0.125**, WF 1.125x naive | **n 8, r +0.034, WF 1.178x naive** |
| `ia_lfl_price_yoy` 2025Q3 | −5.71% on **3** cities | **−8.35% on 2 cities** |
| `ia_lfl_price_yoy` 2024Q4 | 0.00% on **2** cities | 0.00% on **1** city |
| 3Q26 nowcast, demand index (nights / GBV / revenue) | 12.07 / 15.32 / 17.03 | 11.84 / 15.01 / 16.56 |
| 3Q26 nowcast, demand index ex Inside Airbnb (nights) | 10.23 | 9.95 |
| Composite demand / supply / price indexes | lose to naive on every target | **lose to naive on every target** |

`08_q3_2026_guide_reconciliation.csv` is unchanged, and `08_demand_index_quarterly.csv` and
`08_q3_2026_nowcast.csv` — the two WS08 files the driver model reads — changed but **moved no model
output**: `13_driver_model.py` was re-run and `13_model_annual.csv`, `13_model_quarterly.csv`,
`13_valuation_summary.csv` and `13_scenario_grid.csv` came back byte-identical.

**Note edits applied** to `08_altdata-index-and-backtests.md`: WS20's three section-10 rewordings
(finding 6, the guide-reconciliation paragraph and 5-Nov-card item 3 all now say *consistency check,
not a forecast*, with the point that choosing the revenue-minus-GBV gap is what makes it land); the
like-for-like price paragraph restated with the new series and the 1-4-cities-per-quarter caveat; the
component-family best ratio 0.69 -> 0.68 and the Common Crawl survival row restated on WS19's corrected
y/y alignment (0.68 on n 10, r −0.54); and a dated correction bullet in section 9 for the hotel-RevPAR
point-in-time fix.

## 5. Step 4 — WS11 numbers

`11_competition_supply_overlays.py` now consumes the **published** `pair_eligible` / `exclusion_reason`
columns instead of re-deriving the partial-scope join from the snapshot table, cites the exclusion
reasons in its log (103 pairs, 25 dropped, mean retention 0.489 excluded against 0.726 kept), labels
pairs that straddle a listing-count step, and writes two new summary rows.

- **`inside_airbnb_year_ago_retention_six_city_ex_austin`: 0.755 (2025) -> 0.734 (2026)**, n 14 and 34
  pairs, over Chicago / Los Angeles / Nashville / Paris / Rome / San Diego. New-listing share of the
  ending base **0.254 -> 0.254, exactly flat.**
- **`inside_airbnb_year_ago_retention_austin` 2026 = 0.509 now carries a SCOPE ARTEFACT label.** Austin
  stepped from 15,187 listings in Jun 2025 to ~11,000 from Sep 2025 and stayed there; all four 2026
  pairs span the step, so 49-53% "retention" is the step, not churn. Austin has no usable year-ago
  retention until the Sep 2026 dump lands.

The note's headline, bottom line and "For the model" row all move from the seven-city **75.4% -> 71.1%**
to the six-city ex-Austin **75.5% -> 73.4%**, and the paragraph that called Austin "a genuine outlier,
not an artefact" is corrected in place. The regulatory section takes WS22's post-fix numbers: median /
mean / p95 drag **0.150 0.450 0.855 / 0.251 0.752 1.235 / 0.891 2.672 4.011**, EMEA cumulative nights
drag 2028 **−2.03%**, P(loss >1%) **18.9% by 2027 and 71.0% by 2030**, and **77.9%** of the 2027
variance in two EU items (the note's "68%" was a transcription error — the pre-fix file said 75.2%).

## 6. Step 5 — the WS23 / WS24 flags

1. **`15_claim_checks.py` line ~99.** The WS09 claim *"mean absolute day-1 move 7.07% (median 6.87%);
   no implied event premium 60 days out (0.002 pts)"* was scored `confirmed`. The base-rate half is
   right; the options half is **withdrawn** — the 13.38 / 15.65 comparison it cites is between two
   **post-event** expiries, and the old estimator recovered `E x (1 − T_near/T_far)`, not `E`, so it
   could not have detected an event premium. The row is now `wrong`, with the evidence, the rebuilt
   estimator's three irreconcilable specifications (non-positive / 2.31% / 6.73%) and the re-run date.
   Two more rows were restated: WS11's retention claim (now `wrong`, restated ex-Austin) and WS11's
   regulatory claim (stays `confirmed` against WS22's regenerated file). **Tally 84/9/1/4 -> 82
   confirmed / 11 wrong / 1 unsupported / 4 unverifiable** across the same 98 claims. The WS19 integrity
   guard is intact and passes: 98 rows x 7 columns, 16 conflicts CONF-01..CONF-16, no formula-leading
   cell, no embedded newline. `15_red-team.md` carries a second dated amendment banner.
2. **`09_stock_behaviour.py` no longer overwrites the corrected JSON.** Before writing it reads
   `09_implied_move_live.json`; if the file carries `method_version >= 2` (or, for files written before
   that key existed, the WS23 schema keys `event_estimates` / `estimator_source`) it writes its own
   legacy block to **`09_implied_move_live_legacy.json`**, carries the corrected `live_*` columns
   through into the rebuilt `09_implied_vs_realised.csv`, and prints a pointer to
   `23_update_ws09_options.py`. `method_version: 2` was added to `23_update_ws09_options.py` and stamped
   on the existing JSON. Guard fixture: protected on the file as it stands and on the bare WS23 schema;
   overwrites a `method_version: 1` file and an unreadable one.
3. **`15_script_runs.py` absolute paths removed.** All three (`SC`, `OUT`, `SRC`) derive from the repo
   root; the run directory is `<root>/data/cache/15`, overridable with `ABNB_RUNS_DIR` or
   `ABNB_SCRATCH`; a missing `runs.tsv` is now a loud failure that explains the file format instead of
   a `FileNotFoundError` on someone else's profile. Re-run: `15_script_runs.csv` is byte-identical
   (34 scripts, 34 ok).

## 7. Step 6 — synthesis and summary

`research/notes/overnight/14_master-synthesis.md` and `docs/overnight/FINAL_SUMMARY.md` both take
WS20's section-10 line edits, the new model numbers, WS22's regulatory numbers, WS21's retention
numbers and WS23's options verdict. Structure kept; numbers and sentences edited.

- **Nights-surprise drift withdrawn.** Sections 3.2, 3.3 and 6.2 of the synthesis and the "what
  predicts what" list in the summary now say that the 20-day window began at the **pre-release close**,
  and that on an executable next-open entry LOO R² goes +0.156 -> **−0.016** and the walk-forward goes
  0.958x -> **1.076x** a zero baseline. Zero of WS20's 18 primary executable drift specs beat their
  baselines. The summary adds that 73% of the legacy day-1 variance is the overnight gap, so only 3.2
  of the 6.8 points of mean absolute day-1 move was ever capturable.
- **Guide-below-Street restated in all six places it appears**: still **9 of 9** negative, but mean
  **−4.21%** (median −4.42%) on an executable next-open entry rather than −8.90% on the
  pre-release-close convention, **base-rate p 0.038** against ABNB's own **69.6%** rate of negative
  20-day excess on **n 23** (the earlier 0.057 used n 22). The day-1 half collapses: 3 of 9 negative,
  mean +0.91%.
- **The frozen 5 Nov rows** from `20_frozen_q3_2026.csv` are now in the summary's pre-registered card:
  designated **+1.37% revenue surprise (≈$4,805m)** and **+1.83% nights surprise (≈147.6m)**, both
  trailing-4-quarter baselines because nothing beat the baselines in both windows, with 16 feature rows
  stored for scoring on 6 November and two marked PENDING.
- **The guide reconciliation is consistency evidence only**, in both the WS08 note and the summary.
- **The options verdict** replaces section 6.3 of the synthesis: no quotable ABNB event-implied move,
  the 6 Nov 2026 weekly not listed, the only quotable option prices are the raw total-implied-move
  straddles (20 Nov 13.38% of spot, 18 Dec 15.65%, 15 Jan 17.01%), and the re-run window moves to
  26-30 October.
- **Model, regulatory and retention numbers** updated as in sections 3-5 above, including the summary's
  headline football field (**bear $74 / base $157 / bull $228**) and the file-count block
  (26 notes, 59 scripts, 202 data files, 24 figures).
- **A new synthesis subsection 11.5, "The independent audit, findings A01-A13 (WS19-26)"**, ten numbered
  items plus the verification block and an explicit "still open" paragraph.

---

## 8. A01-A13, final status

| id | finding | owner | status at 7 Sep 2026 | what remains |
|---|---|---|---|---|
| **A01** | Backlog feature divides by the target quarter's actual revenue | WS19 (+WS26) | **Closed.** `bl_unearned_to_next_rev_lag1` replaced by a prior-quarter denominator; acceptance test perturbs the target-quarter actual and the new feature does not move. WS26 closed two more members of the same family (`pr_hotel_revpar_yoy`, `ia_lfl_price_yoy`) | Nothing. The leaky feature was never a reported survivor |
| **A02** | Reaction tests are LOO, and the return window starts before the predictor exists | WS20 (+WS26) | **Closed at the conclusion level.** Executable open-entry convention built (`20_executable_returns.csv`), the reaction work split into a pre-earnings forecast task and a post-release drift task, 391-row prediction ledger, 4/4 leakage perturbation checks pass. The nights-drift result is **withdrawn** in the synthesis and the summary | The frozen spec must be scored on 6 Nov before anything is re-selected. Task B has not been widened to an open-to-open event-time panel |
| **A03** | Window sensitivity, multiple testing, data vintage | WS20 (+WS26) | **Closed as far as it can be tonight.** `20_experiment_spec.json` (`ABNB-WS20-v1`) frozen before 5 Nov; `20_vintage_register.csv` labels every series reconstructible or APPROXIMATION and excludes Google Trends outright; `20_incremental_value.csv` scores 77 baseline-plus-feature tests; the four sentence rewordings are applied | **No true vintage series has been reconstructed** (Eurostat revision archive or FRED ALFRED). Until one is, the Eurostat and macro results rest on a current-vintage approximation |
| **A04** | Partial Inside Airbnb snapshots contaminate year-ago pairs | WS21 (+WS26) | **Closed.** Eligibility computed in `inside_airbnb_supply_panel.py` and published as `pair_eligible` / `pair_eligible_pit` / `exclusion_reason`; 17-check fixture passes; WS08, WS11, the claim checks, the synthesis and the summary all consume it | **Scope reduction and genuine contraction are not separable from listing counts alone** — `span_step_warning` marks the ambiguous pairs rather than deciding. WS06's per-city-dump level series (`06_price_per_unit_panel.csv`, `06_quote_discount_panel.csv`) still lack the joined scope flag; `data/external/inside_airbnb_like_for_like.csv` is a stale copy; `01_data_census.py` rows D122-D124 and `data/README.md` line 46 do not list the new columns |
| **A05** | Common Crawl four-**row** shift is not four **quarters** | WS19 | **Closed.** Reindexed onto a contiguous quarterly `PeriodIndex`; gaps stay `NaN`. 7 of 12 comparisons were wrong; 2024Q1 flips −3.100 -> +2.767 | Do not quote the old `cc_survival_yoy_pts` values. WS26 updated the WS08 note's 0.69 -> 0.68 / n 11 -> n 10 |
| **A06** | Regulatory tail sampled without its parent; Barcelona conditional | WS22 (+WS26) | **Closed.** Three defects reproduced then repaired with no probability, loss range, correlation or exposure anchor changed; 77 acceptance checks, 0 failures; an assertion now prevents a tail probability exceeding its parent's. Model input, WS11 note, claim check, synthesis and summary all updated | The register's probabilities remain **single-analyst estimates with no market to score them against**; within-horizon timing and a reversal/lapse state are unmodelled; the acknowledged EU-AHA / national-event double-count still biases the 2030 mean high |
| **A07** | Reproducibility: deps, paths, build order | WS24 (+WS26) | **Closed for this tree.** `docs/overnight/BUILD.md` is the ordered build graph; `requirements.txt` de-duplicated and completed; the Excel COM driver is in the repo as `17_recalc_dump.ps1`; seven scripts lost their absolute paths in WS24 and the **last two in WS26** (`08_altdata_backtests.py`, `15_script_runs.py`) | The audit's dependency complaint is a **MAIN-tree** problem and is unfixed there. `data/cache/` is gitignored, so a clean checkout re-downloads the FRED series and cannot reproduce `15_script_runs.csv` without re-running all 34 scripts. Two non-pip prerequisites (poppler `pdftotext`, desktop Excel) are documented, not automated. The stale 20-quarter main-tree `abnb_quarterly_cost_stack_exsbc.csv` should be retired in favour of this tree's 22-quarter file |
| **A08** | Options event-variance identification | WS23 (+WS26) | **Closed as a method; the number is deliberately absent.** Estimator rewritten to fit `sigma_i^2*T_i = b*T_i + E*d_i` over every eligible maturity, 25/25 synthetic acceptance checks, strict post-event expiry eligibility, verified same-strike straddles, negative fits returned rather than floored. The old headline is **withdrawn** in WS09's note, the claim checks, the synthesis and the summary, and `09_stock_behaviour.py` can no longer overwrite the corrected artefacts | **`E` is not identified for ABNB today** (specs span non-positive to 6.73%) because the 6 Nov 2026 weekly is not listed. Re-run in the week of **26-30 October 2026**; then check `event_confidence`, which should upgrade to `company_confirmed` |
| **A09** | Two malformed records in `16_news_since_5sep.csv` | WS19 | **Closed.** Both publisher fields quoted; the file parses as 20 rows x 7 fields in strict `csv.reader` and in pandas, every value preserved | Nothing |
| **A10** | Reverse-DCF `#DIV/0!` when growth equals the discount rate | WS19 (+WS26) | **Closed.** The ten-year leg is an explicit discounted sum rather than the closed-form annuity, continuous through `g = coe`; the Gordon terminal keeps its `/(coe − g)` deliberately. Re-verified after every WS26 rebuild: **0 error cells in 5,553** | Nothing. Flexing the cost of equity in Excel is safe |
| **A11** | Rerun script cannot append a quarter; stale derived surprises | WS24 | **Closed.** `16_merge_and_rerun.py` has a real `--append` path with schema and uniqueness validation, source-and-vintage enforcement, a frozen pre-event forecast a post-event refit cannot overwrite, and derived surprise fields recomputed from primitives on every run; 33/33 checks pass; the latent `KeyError` in the new-quarter branch is fixed | **`16_web-gap-fill.md` still quotes the pre-regeneration EPS rows** (n 17 vs the panel's 20 usable EPS pairs). The specs stay uninformative either way, so no conclusion moves, but the note's numbers are stale. Use `--append`, not a default re-run, after 5 Nov |
| **A12** | Valuation-date and share-count conventions | WS25 (+WS26) | **Closed as a decision, and now enforced in arithmetic.** All four conventions are written into `model/assumptions.md`; `25_valuation_conventions.csv` carries the per-lens dates; and WS26 removed the one place where the convention and the arithmetic disagreed by discounting the FY2028E lens to the common target date, keeping the undiscounted value as a labelled sensitivity | The **period-end fully diluted share bridge is proposed, not built** (10-Q cover-page shares plus the equity-incentive footnote, rolled on the disclosed unrecognised-SBC recognition period). Expected effect: low single-digit millions of shares, under 1% on price. The `DCF fade period (years)` input is still inert in Excel and live in Python — treat it as read-only at 10 |
| **A13** | Audit scripts never exit nonzero | WS24 (+WS26) | **Closed.** `17_excel_audit.py` and `17_scenario_switch.py` return 0 / 1 / 2, proved both ways against a deliberately corrupted workbook copy (7/7 cases in `24_exit_code_tests.csv`). WS26 additionally removed the hard-coded `Valuation` row addresses in `17_scenario_switch.py` that produced 12 spurious mismatches the moment a row was inserted | Before quoting any workbook number, run both scripts and check the **exit status**, not the log — and regenerate the three Excel dumps first if `13_excel_builder.py` has been re-run |

Two findings from the same handoff that are not in the A-series: **S01** (a red-team allegation that was
itself wrong) closed in WS19, **S02/S03** (stale summary counts, a superseded-note marker) closed in
WS24/WS25 and refreshed again here. **K01** (the `15_cross_note_conflicts` complaint) closed in WS19 —
the file was never truncated; Excel was silently evaluating sign-leading cells.

## 9. Corrections to existing work

- `analysis/src/overnight/17_scenario_switch.py` had **hard-coded `Valuation` row addresses**. It is
  another workstream's file; the fix was unavoidable because WS26's own edit exposed it, and it is
  recorded here and in `26_change_ledger.csv` (`X05`) rather than left silent.
- `research/notes/overnight/11_competition-supply-and-overlays.md` said **"68% of the 2027 variance"**;
  the pre-fix contributions file gave 75.2% and the post-fix file gives 77.9%. WS22 found this; WS26
  applied it.
- `research/notes/overnight/16_web-gap-fill.md` quotes EPS-surprise rows superseded by WS24's
  regeneration of `16_reaction_tests.csv` (n 17 -> 20 / 20 / 19 at 1d / 5d / 20d). Not edited — it is
  WS16's note and no conclusion moves — but a reader should take the CSV over the note.
- `research/notes/overnight/06_consumer-choice-and-willingness-to-pay.md`'s per-city-dump level series
  still need the scope flag joined (WS21 section 7). The hedonic premia themselves are unaffected,
  because WS06 demeans inside each city-dump and partial dumps are uniform subsamples.

## 10. For the model

| Parameter | Value | Unit | Source |
|---|--:|---|---|
| Regulatory nights drag, incremental pp, FY26 / FY27 / FY28 (NA / EMEA) | 0.03/0.36, 0.05/0.71, **0.07/0.96** | pp of y/y growth | `11_regulatory_overlay.csv` post-WS22; `13_driver_model.py` `REG_DRAG_PP` |
| FY2028E lens treatment | discounted **one year at the scenario cost of equity** | convention | `model/assumptions.md`, conventions decision 1 |
| Base football field low / mean / high | 110.58 / **156.79** / 196.92 | $/share | `13_valuation_summary.csv` |
| Bear football field low / mean / high | 37.23 / **74.18** / 108.46 | $/share | same |
| Bull football field low / mean / high | 176.49 / **228.18** / 281.01 | $/share | same |
| Base EV / adj. EBITDA FY2027E lens (unchanged) | 180.88 | $/share | same |
| FY2028E lens, undiscounted (sensitivity, not in the field) | 103.64 / 217.59 / 289.09 | $/share | same |
| FY2028E base revenue / adj. EBITDA / FCF per share | 17,947.1 / 6,703.9 / 11.041 | $M, $M, $ | `13_model_annual.csv` |
| 4Q23 ex-SBC cash costs, ops / pd / sm / ga | 254 / 253 / 391 / 1,142 | $M | `abnb_quarterly_cost_stack_exsbc.csv` |
| Six-city ex-Austin year-ago retention, 2025 -> 2026 | 0.755 -> **0.734** | share | `11_supply_economics.csv` |
| Guide-below-Street 20-day excess, executable entry | **−4.21** (9 of 9), base-rate p 0.038, n 23 | % mean | `20_convention_restatement.csv` |
| ABNB event-implied move, 5 Nov print | **not identified** | — | `23_options_event_estimates.csv` — do not substitute a number |

## 11. For the 5 Nov card

- The designated forecasts are baselines, not models: **revenue surprise +1.37% (≈$4,805m)** and
  **nights surprise +1.83% (≈147.6m)**, from `20_frozen_q3_2026.csv`. Score the 16 feature rows against
  them on 6 November, **before** touching `spec_id ABNB-WS20-v1`.
- **Do not size a trade on a day-1 reaction model.** Three quarters of the historical day-1 signal is an
  overnight gap nobody can enter.
- The one usable rule is the binary risk flag: a Q4 guide midpoint below the then-current Street revenue
  number has been followed by a negative 20-day excess return 9 of 9 times, mean **−4.21%** on an
  executable entry, base-rate p **0.038**. Use it for sizing, not as a short.
- **Use the 7.07% historical base rate for the day, not an implied move.** Re-run
  `analysis/src/abnb_options_ledger.py` and `23_update_ws09_options.py` in the week of 26-30 October,
  once the 6 Nov weekly lists; only then is the cheap/rich test (below ~7% cheap, above ~9% rich)
  available, and only if the three specifications agree within ~1.5 points.
- Nothing in the cost-stack, regulatory or Inside Airbnb repairs changes a Q3 2026 line. Two negatives
  to carry: the Inside Airbnb supply-exit story (Paris 33%, Nashville 44%, Chicago 40%) **is not real**,
  and Austin has no comparable year-ago pair until the Sep 2026 dump.
