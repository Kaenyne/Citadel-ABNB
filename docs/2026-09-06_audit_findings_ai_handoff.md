# ABNB research audit: repair and validation handoff for another AI

**Purpose:** turn the independent read-only audit into an actionable repair backlog. The research objective is to determine whether the team's alternative data can predict future ABNB stock moves through better earnings and guidance forecasts.

**Prepared:** 6 September 2026. Follow-up verification at approximately 17:44 UTC / 13:44 ET.

**Authorization for this handoff:** the user requested this document after requesting a read-only audit. Creating this document is the only modification made by its author. Proposed repairs below have not been implemented by the audit author. This document is not an instruction to merge branches, publish research, acquire paid data, or execute trades.

## 1. Read this first: the state changed after the original audit

The original audit identified a live FY2026 share-count defect and unfinished WS16/17 integration. Another session subsequently repaired the share-count calculation and committed the overnight follow-ups. **Do not blindly reproduce the original audit's open-status list.**

| Repository alias | Absolute directory | HEAD at follow-up |
|---|---|---|
| `MAIN` | `C:/Users/krish/citadel-abnb` | `e9c840d723e5ae176fec2e3c70f80dfdedc4b9c8` |
| `OVERNIGHT` | `C:/Users/krish/citadel-abnb-overnight` | `77037c2d93622fcac1941e980ceadd5579dac594` |

`OVERNIGHT` is on `krish/overnight-synthesis`. Its latest commit is **“Follow-ups 16-18: web gap fill, Excel COM audit, share-count fix.”** It was clean at the follow-up check. MAIN still contains the older uncommitted research/model files. Paths below use these aliases; they are directory labels, not shell variables that already exist.

At the original final inventory, ten worktrees were accessible: MAIN had 163 uncommitted files (4 modified, 159 untracked), OVERNIGHT had 20 (3 modified, 17 untracked), and the other eight worktrees were clean. Relevant committed forecasting dependencies were inspected because the uncommitted outputs rely on them. This was not a line-by-line re-audit of every committed file in every branch.

### Current disposition of the original findings

| ID | Priority | State | Finding |
|---|---|---|---|
| A01 | P1 | Open; code rechecked | Future actual revenue leaks into a purported pre-print backlog feature |
| A02 | P1 | Open | Reaction validation mixes future training observations and a return window beginning before the predictor exists |
| A03 | P1 research gate | Open | Incremental predictive value remains window-sensitive; selection and data-vintage controls are incomplete |
| A04 | P2 | Open; code rechecked | Inside Airbnb partial snapshots contaminate retention and matched-review comparisons |
| A05 | P2 | Open; code rechecked | Common Crawl four-row shift is not necessarily four calendar quarters |
| A06 | P2 | Open; code rechecked | Regulatory event simulation does not implement stated conditional dependencies |
| A07 | P2 | Open; partially improved | Canonical checkout, dependencies, raw inputs, and audit reproduction are not consolidated |
| A08 | P2 | Open; code rechecked | Options event-variance estimator and expiry selection are inadequate for the stated interpretation |
| A09 | P2 | Open; file rechecked | WS16 news CSV has two malformed records |
| A10 | P2 | Open; code rechecked | Excel reverse DCF divides by zero when finite-period growth equals the discount rate |
| A11 | P2 before next print | Open; confirmed in follow-up | WS16 rerun script cannot append a new earnings quarter and can retain stale derived surprises |
| A12 | Model convention | Open question, not a proven arithmetic error | DCF/exit-lens valuation dates and share-count definitions need explicit treatment |
| A13 | P2 validation infrastructure | Open | Audit scripts report failures but do not reliably signal failure through process exit status |
| R01 | Previously P2 | Resolved in OVERNIGHT; stale MAIN remains | FY2026 double-counted first-half net share reduction |
| R02 | Mechanical/integration | Resolved in OVERNIGHT | Scenario selector, several workbook controls, WS17 note existence, and WS16 synthesis edits |

P1 means a blocker to claiming predictive validity. P2 means a confirmed implementation or interpretation defect that should be corrected before relying on affected outputs. A model-convention question requires an explicit decision and consistent labels, not an arbitrary silent numerical change.

## 2. Overall judgment on the research objective

There has been substantial useful progress: structured alternative-data panels, provenance records, matched listing cohorts, guidance and consensus history, revenue and margin decompositions, regional builds, and a live Excel/Python model. Negative findings about weak data are progress if the tests are valid and their limits are preserved.

The work does **not yet establish** the full predictive chain:

1. Information demonstrably available at a chosen pre-release decision time;
2. Incremental improvement in forecasts of earnings, operating KPIs, or next-quarter guidance relative to simple and consensus-based baselines;
3. A forecast of the surprise relative to expectations available at that same time;
4. Incremental prediction of returns measured from an executable entry time;
5. Stability across evaluation windows and a prospectively frozen test.

The distinction matters. Explaining a released surprise is different from forecasting that surprise. Reproducing management's guide with a driver identity is useful reconciliation, but it is not independent evidence that alternative data predicts a beat. A lower assumed exit multiple changes valuation without proving an earnings forecast edge. Agreement between Excel and Python verifies consistency, not the economic validity of shared assumptions.

## 3. A01 — Future revenue in the backlog feature

**Evidence and locations**

- `MAIN/analysis/src/abnb_eu_platform_and_backlog.py`, approximately lines 159–161: creates `next_q_revenue_musd` with a negative shift, then `unearned_to_next_q_revenue = unearned_fees_musd / next_q_revenue_musd`.
- `OVERNIGHT/analysis/src/overnight/08_altdata_backtests.py:116`: `F["bl_unearned_to_next_rev_lag1"] = b["unearned_to_next_q_revenue"].shift(1)`.
- Relevant outputs: `OVERNIGHT/data/processed/overnight/08_feature_tests_all.csv`, backlog test subsets, and any notes or indexes that consume those test results.

The original ratio at quarter q is `unearned[q] / revenue[q+1]`. Moving the ratio one row forward makes the feature at target quarter t equal to **`unearned[t-1] / revenue[t]`**. The numerator is historical; the denominator is the future target quarter's actual revenue. A lag applied after forming the ratio does not remove leakage.

The original audit found six feature/target/window test rows using this feature. It was not the principal reported positive survivor; nevertheless neither positive nor negative results from it are legitimate pre-print evidence.

**Required repair**

1. Remove this feature from predictive evaluation, or replace its denominator with a value available at the decision cutoff: trailing revenue, prior-quarter revenue, or a separately frozen forecast. Name the replacement to reflect its actual definition.
2. Preserve a next-quarter-actual ratio only as a clearly labelled retrospective diagnostic if useful.
3. Audit the entire lineage of pre-print features, not just final `.shift()` calls. Derived denominators, fitting windows, revised data, and availability dates can each introduce future information.
4. Regenerate affected test tables and revise claims/counts that depended on the invalid feature.

**Acceptance checks**

- A small fixture with known quarterly unearned fees and revenue proves the replacement's exact indexing.
- Perturb target-quarter and later actual revenues while holding all information available at the forecast cutoff fixed. The feature and frozen forecast at that cutoff must remain unchanged.
- The predictive feature registry records observation period, release time, and availability time; no row merely asserts “prior quarter” without checking the expression's operands.
- No predictive output retains the old feature under a misleading “available before print” label.

## 4. A02 — Earnings reaction tests are not yet a tradable out-of-sample test

**Evidence and locations**

- `OVERNIGHT/analysis/src/overnight/04_reaction_vs_consensus.py:39`, `loo_r2()`: each observation is predicted from a fit using every other observation, including future quarters.
- `MAIN/analysis/src/abnb_from_theo_guidance.py:29`, `build_reactions()`: imports the historical return-window definitions.
- `MAIN/theos-past-research/src/abnb_guidance/market.py:44`: return uses the close before the reaction session as its starting price.
- `OVERNIGHT/data/processed/overnight/16_reaction_tests.csv`: refreshed WS16 results.

The selected nights-surprise relationship has n=18, R² approximately 0.2199, LOO R² approximately 0.1327, and a refreshed permutation p-value approximately 0.0560. The post-2022 subset has n=11 and LOO R² approximately 0.1779. These are exploratory results, not proof of a strategy.

There are two distinct timing defects in interpreting them as predictive alpha:

1. Leave-one-out is cross-validation, but it is not a historical trading simulation: future observations influence coefficients for earlier observations.
2. Actual nights surprise is available only when the print is released. A return beginning at the pre-release close includes a price jump that cannot be earned using knowledge of that released surprise.

The audit also tried chronological expanding fits for the already-selected nights-surprise relationship. With initial training lengths of 6, 8, and 10 observations, the prediction-error ratios versus an expanding mean were approximately 0.885, 0.897, and 0.895 (12, 10, and 8 evaluated observations respectively). **Do not claim that chronological testing killed the relationship.** This is modest positive evidence, but feature selection was already performed using the full history, and the predictor/entry-time mismatch remains.

**Required repair**

- Separate a **pre-earnings forecast task** from a **post-release reaction/drift task**.
- For the pre-earnings task, forecast the KPI/guidance surprise using only data and consensus available at the pre-release cutoff. Do not replace that forecast with the subsequently observed surprise.
- For a post-release task, use actual released values but start returns after a defensible executable entry time. Choose next open, a timestamped post-release quote, or a later close explicitly. Do not silently label a pre-close-to-20-day return “drift.”
- Use rolling or expanding temporal validation. Hyperparameter/feature selection must occur within the training history, or freeze a small specified candidate set before evaluation.
- Retain LOO as a supplementary descriptive diagnostic if desired; change language that treats it as the sole out-of-sample proof.

**Acceptance checks**

- Each prediction row records decision time, last permissible training label, forecast values, consensus vintage, entry time/price, and return endpoint.
- Assert all training outcomes used were known by decision time. Account for overlapping 20-day labels when necessary.
- Perturb future quarters and verify earlier stored predictions remain invariant.
- Report baseline and candidate errors on identical dates; provide per-event predictions, not only aggregate R².
- Report how many events remain after realistic timing and missing-data filters.

## 5. A03 — Window sensitivity, multiple testing, and data vintage remain research gates

**Current evidence**

The alternative-data study contains 598 tests. The reaction rerun contains 97 specifications/test rows, and the transcript study explored many more. These rows are not all independent hypotheses, but choosing a winner from them still creates selection risk. Existing notes acknowledge aspects of this problem; that acknowledgement must survive in the final pitch and model labels.

The funds-held-for-clients lagged growth signal illustrates the issue. For next-quarter revenue growth, the original audit reproduced approximately:

| Evaluation setup | Evaluated observations | RMSE / naive | RMSE / AR(1) |
|---|---:|---:|---:|
| Longer window, walk-forward beginning 2023Q1 | 14 | 1.69 | 1.85 |
| Later window, walk-forward beginning 2024Q1 | 10 | 0.60 | 0.59 |

Use `08_feature_tests_all.csv` and `08_survivor_robustness.csv` to verify exact row definitions before quoting these numbers. The key conclusion is sensitivity to the evaluation period, not a universal negative verdict on the feature. Also avoid combining n=14 from one window with a 0.60 ratio from another in a headline.

Expanding transformations are a useful improvement, but a current downloaded historical series is not automatically the series available at a historical decision date. Revised macro data and normalized search histories need vintage treatment. Quarterly timestamps alone do not establish publication availability. No newly confirmed leak is alleged for every series; the required evidence is currently incomplete.

**Required repair / completion**

1. Define a limited primary candidate set and primary target/horizon before the next prospective observation. Keep exploratory tests in a separate ledger.
2. Freeze transformations, weights, feature selection, minimum training size, missing-data policy, and evaluation periods.
3. Store release/vintage metadata or conservatively lag series whose vintage cannot be reconstructed. Label reconstruction approximations explicitly.
4. Compare earnings forecasts against last quarter, prior year, simple autoregression, management guide, guide plus historical cushion, and available contemporaneous consensus. Use the baselines relevant to each target rather than forcing every one onto every target.
5. Evaluate incremental value: baseline plus alt data versus the same baseline without alt data on the same events.
6. Publish window sensitivity and uncertainty alongside the preferred window. Treat prospective validation as the strongest next evidence, not a retroactive rename of an explored sample.

**Acceptance criteria**

- A machine-readable experiment specification and prediction ledger exist before the next print.
- Every headline metric points to a precise test row and evaluation dates.
- “Not significant” is not rewritten as “the data can never work”; “selected positive” is not rewritten as “proven alpha.”
- A guide-reconciliation scenario is labelled as such. In WS08, the combination of guide-like nights +11%, estimated ADR +4.05%, and a chosen zero revenue-minus-GBV gap reproduces the guide midpoint. That is useful consistency evidence, not an independent demonstrated beat forecast.

## 6. A04 — Partial listing snapshots contaminate year-over-year comparisons

**Evidence**

`MAIN/analysis/src/inside_airbnb_supply_panel.py` constructs year-ago pairs at approximately lines 336–344, calculates `partial_scope` around lines 348–356, and selects all year-ago pairs for retention/matched-review charts around lines 388–392. It applies the full-scope filter to snapshot-level charts, not to those pair-level charts.

The original audit joined scope flags onto both endpoints and found **25 of 103 year-ago pairs** touched a partial snapshot. A concrete example is Paris: roughly 86,064 listings on 3 March 2025 versus a partial 38,075-listing snapshot on 21 March 2026, producing roughly **33.15% retention**. Later full snapshots are much larger. That comparison cannot establish the implied mass exit of listings.

Relevant artifacts:

- `MAIN/data/processed/inside_airbnb_city_snapshots.csv`
- `MAIN/data/processed/inside_airbnb_like_for_like.csv`
- `MAIN/analysis/figures/inside_airbnb_retention_yoy.png`
- `MAIN/analysis/figures/inside_airbnb_reviews_ltm_yoy.png`
- `MAIN/research/notes/2026-09-05_inside-airbnb-supply-panel.md`

**Required repair**

- Attach coverage/scope flags for both endpoints before selecting or publishing pairs.
- Exclude non-comparable pairs from a market-retention interpretation, or show them separately with explicit scope warnings. Preserve the raw pair data rather than deleting inconvenient observations.
- Apply an explicit pair-eligibility policy to matched reviews and prices too. Matching IDs controls listing identity, but does not make a selected surviving subset representative of the whole market.
- Preserve the existing same-price-basis check. It usefully avoids interpreting a fee-inclusive quote-format change as price inflation.
- Do not infer global realized pricing power from the four-city historical price subset. Describe it as quoted prices on observed matched listings, with coverage and dates.

**Point-in-time complication**

The current partial-scope heuristic compares a dump to the maximum listing count within **plus or minus 200 days**. Future snapshots can therefore change the historical classification. This is acceptable for a labelled retrospective quality-control analysis, but cannot be silently used as information known at an earlier trading cutoff. Predictive replay needs a cutoff-specific coverage decision or archived contemporaneous classification.

**Acceptance checks**

- Both endpoint flags and an exclusion reason are present in the pair table.
- The Paris partial comparison is excluded from the clean retention chart or unmistakably identified as non-comparable.
- A fixture containing a known partial dump does not create an apparent market exit signal.
- Coverage changes and data corrections cannot silently alter a previously frozen prediction.

## 7. A05 — Common Crawl year-over-year alignment

**Location:** `OVERNIGHT/analysis/src/overnight/08_altdata_backtests.py:221–224`, `cc_features()`.

Surviving informative crawls are grouped by quarter, then the quarterly observations are shifted by four rows. Missing quarters mean that four rows need not equal one year. Examples identified in the original audit include 2023Q4 being compared with 2022Q3, 2026Q1 with 2024Q4, and 2026Q3 with 2025Q2.

**Required repair:** reindex to a contiguous quarterly PeriodIndex before computing the four-quarter difference. Leave missing observations missing unless a separately justified imputation rule is specified. Do not invent a crawl observation by forward-filling just to obtain a YoY feature.

**Acceptance:** a fixture with a missing quarter proves that a comparison is either exactly t versus t−4 calendar quarters or is missing. Recompute affected Common Crawl tests and composites; retain capture/coverage limitations in interpretation.

## 8. A06 — Regulatory probability dependencies

**Location:** `MAIN/analysis/src/abnb_regulatory_forecast.py`, `EVENTS` and `draw()` (approximately lines 39–65 and 108–129). Also inspect the corresponding OVERNIGHT copy and the WS11 overlay that consumes regulatory outputs when implementing a fix.

### A06a: EU tail without prerequisite

`EU-TAIL` is described as conditional on adoption/enforcement of `EU-AHA`, but `draw()` samples it separately using correlated uniforms and never gates it on the parent. Correlation is not a logical prerequisite.

The original 200,000-draw reproduction found:

- 2027: tail without parent in approximately 1.0845% of all draws, or 54.02% of tail occurrences.
- 2030: tail without parent in approximately 1.731% of all draws, or 21.72% of tail occurrences.

**Repair:** explicitly model the parent-child relationship. First decide whether the supplied 2%/8% probabilities are intended as unconditional tail probabilities or probabilities conditional on the parent. Simply adding a boolean gate changes the marginal probability and may not implement the intended assumptions. Record both conditional and resulting marginal probabilities.

### A06b: Barcelona conditional probability differs from the rationale

The partial branch is gated on absence of the full branch. The rationale states `0.55 * (1 − 0.45)`, approximately 30.25% effective probability. Because the pre-gate draw is correlated with the full-branch draw, the reproduced effective probability is approximately **23.05%**.

**Repair:** sample the partial branch under a genuinely specified conditional distribution, or retain the correlated construction and revise the stated probabilities/rationale to its actual implications. Do not claim the simple product while using a different joint law.

### A06c: Cumulative horizons are not a coherent path

Residual draws are renewed for 2027 and 2030. Approximately 3.01% of reproduced draws have the EU parent occurring by 2027 but absent by 2030. If these are cumulative “adopted/enforced by” events, a common path should be monotone. If reversal is intended, it needs a named transition; if the horizons are independent marginal scenarios, do not describe them as a simulated longitudinal path.

**Acceptance checks for A06**

- Zero child-without-parent occurrences.
- Zero mutually exclusive Barcelona full/partial overlaps.
- Simulated conditional and marginal probabilities agree with the declared targets within Monte Carlo sampling uncertainty.
- Monotone by-date events unless an explicit reversal state exists.
- Recompute contribution tables, quantiles, profile chart, WS11/model overlays, and affected prose. Keep revenue loss, EBITDA compliance cost, and one-off cash impacts separate.

The probabilities and impact distributions remain scenario assumptions; repairing probability mechanics does not create empirical calibration. The matched licensing/listing cohorts are useful exposure evidence, but do not by themselves establish realized lost transactions or causal revenue losses.

## 9. A07 — Reproducibility and competing versions

**Confirmed problems in MAIN**

- `requirements.txt` lacks `statsmodels`, `scipy`, and a Parquet engine (`pyarrow` or `fastparquet`) needed by new scripts. The audit interpreter could not import the relevant missing packages.
- Referenced builders absent from MAIN include `analysis/src/abnb_costlines_from_xbrl.py`, `abnb_kpi_vs_category.py`, `abnb_margin_bridge.py`, and `capital_return_panel.py`.
- Referenced FRED/BEA inputs are missing from MAIN. `data/README.md` says the small raw extracts are kept in Git, but `.gitignore` excludes `data/raw/*` without the stated exceptions.
- MAIN lacks the integrated `analysis/src/overnight/` workflow. A clean checkout of MAIN is not equivalent to the author's machine with sibling worktrees and raw-data junctions.
- The older MAIN driver applies full-year cash/share flows to a midyear starting balance and omits RSU withholding from cash. The later OVERNIGHT cash fix and WS18 share fix must not be mistaken for fixes to MAIN's old source/output files.

The old cash error includes approximately $818M of repeated H1 FCF less buybacks in FY2026, plus omitted annual RSU tax withholding (roughly $0.65–0.73B in the old base projections). These are defects of the old version; **do not apply another cash correction to the already corrected current overnight model**.

**Audit reproduction gaps**

- `16_merge_and_rerun.py` hard-codes the absolute OVERNIGHT path.
- `17_scenario_switch.py` defaults to a specific user's transient scratch directory.
- The native Excel recalculation driver is referenced as `scratchpad/17/recalc_dump.ps1`, not a durable self-contained repo workflow.
- Published saved comparisons are valuable evidence, but a teammate should be able to regenerate them with documented prerequisites.

**Required repair**

1. Choose and document the authoritative integrated model/research entry point. Preserve older analyses as clearly labelled historical/reference artifacts if useful.
2. Consolidate code and input manifests through the normal authorized branch workflow. Do not copy all raw data indiscriminately: licensed material can remain external with a documented retrieval/access contract.
3. Declare direct runtime dependencies and document installation/runtime assumptions.
4. Resolve paths relative to the project or explicit CLI/configuration inputs. Keep machine-specific scratch locations out of default reproducibility contracts.
5. Provide an ordered build graph: input acquisition or availability check, normalized panels, feature tests, model, workbook, native Excel dump, reconciliation, notes/summary regeneration.
6. Update stale documentation. The WS17 note is now a historical pre-WS18 audit and still says the share error is open; a clear superseded-by marker is preferable to letting another AI reopen the repaired item.

**Acceptance:** run the documented pipeline in an isolated checkout with only declared dependencies and explicitly supplied inputs. Fail clearly on missing inputs; do not fall back silently to sibling directories or stale outputs. Confirm which artifacts are regenerated and which require external licensed access.

## 10. A08 — Options event-implied move

**Location:** `MAIN/analysis/src/abnb_options_ledger.py:69–75`.

The code estimates event variance as `(sigma_near² − sigma_far²) * T_near`, floors negative results to zero, and multiplies its square root by 0.8. Both expiries can include the same earnings event, so the farther volatility is not an event-free baseline.

Under a simplified common background variance b plus one event variance E:

`sigma_near² = b + E/T_near`

`sigma_far² = b + E/T_far`

The implemented difference yields `E * (1 − T_near/T_far)`, not E. This algebra shows the identification problem even before market complications. Real term structure may contain other events, changing background variance, stale quotes, and liquidity effects.

Expiry selection uses proximity to a target date rather than a strict after-confirmed-earnings condition. Existing EXPE/HLT fallbacks were before the intended print. Independent nearest-strike call/put selection also merits checking before labelling their sum an ATM straddle.

**Required repair**

- Require a verified or explicitly estimated event timestamp and record its confidence.
- Ensure the event-containing expiry truly follows the event; otherwise report the event estimate unavailable.
- Use an explicit total-variance/event model with enough maturities and declared assumptions, or remove the isolated event-move estimate and report raw straddle/IV measures with accurate labels.
- Store bid/ask/mid, strikes, observation time, and quote-quality criteria. Do not equate a zero floor with no earnings premium.

**Acceptance:** synthetic known-background/known-event examples recover the intended quantity; expiries that precede the event fail eligibility; zero/negative estimates are labelled appropriately; same-strike call/put construction is verified if called a straddle.

## 11. A09 — Malformed WS16 news CSV

**File:** `OVERNIGHT/data/processed/overnight/16_news_since_5sep.csv`, physical lines 15 and 16 at audit time.

The publisher field contains `TipRanks (estimated, not company-confirmed)` without CSV quoting. Those records have eight fields against a seven-field header. A standard `pandas.read_csv()` fails with `Expected 7 fields in line 15, saw 8`. This remained present after commit 77037c2.

**Repair:** quote/serialize the publisher field correctly, preferably write the table with a CSV serializer rather than manual string concatenation. Preserve all values and distinguish estimated event dates from source publication dates.

**Acceptance:** strict CSV parsing succeeds; all nonempty records have the header width; the two publishers remain single fields; URL and status columns do not shift; row count and intended content are preserved.

## 12. A10 — Reverse-DCF boundary case

**Location:** `OVERNIGHT/analysis/src/overnight/13_excel_builder.py`, nested `rdcf()` around lines 960–970; compare `13_driver_model.py`, `dcf_constant()` around line 548.

The workbook uses a closed-form finite annuity containing division by `cost_of_equity − growth`. When these rates are equal, it produces `#DIV/0!` even though the finite stream has a valid value. Example: change the base cost of equity to 11%; the existing 11% growth ladder row reaches this case. The current default of 10.5% avoids every ladder equality and therefore does not test the bug.

The Python constant-growth implementation already handles the equal-rate limit through `a = (1+g)/(1+coe)` and an equality branch. Excel and Python therefore differ in this input region.

**Repair:** use an explicit finite sum or a numerically stable limit branch in Excel. Retain the existing distinction between finite-horizon growth equalling the discount rate (valid) and Gordon terminal growth equalling/exceeding the discount rate (invalid under this perpetual-growth formulation).

**Acceptance:** test exact equality and nearby rates on both sides, compare Excel to a direct finite discounted sum and the Python mirror, and verify continuity. Invalid terminal assumptions should produce a meaningful validation failure rather than a plausible price.

The offline reverse-DCF solved-growth cells now have a live staleness check, which is an improvement. They still do not automatically solve again when inputs change. Preserve that distinction in usability/documentation claims.

## 13. A11 — The next-print rerun instructions do not match the script

**Location:** `OVERNIGHT/analysis/src/overnight/16_merge_and_rerun.py`, approximately lines 25–60. Related instructions: `research/notes/overnight/16_web-gap-fill.md`, “What to build next.”

The note suggests appending the next quarter and rerunning. The script only patches cells in a fixed historical base and raises `SystemExit("unknown quarter ...")` when an additions record refers to a new quarter. It cannot currently deliver the advertised prospective next-print update.

There is a second failure mode: derived guide surprise is recalculated only when its existing value is missing. Updating a nonmissing consensus/guide input can leave the old nonmissing surprise unchanged unless the additions table also patches it. The same general dependency issue applies to other derived surprise fields. The current hand-curated additions may be internally consistent; the bug concerns general update behavior and the promised next use.

**Required repair**

- Provide an explicit append-new-event path with schema validation, uniqueness checks, source/vintage fields, and required actual/consensus/guide values.
- Recompute derived fields from their primitives after applying changes, using a clear policy for sourced versus calculated values.
- Preserve the pre-event frozen forecast separately from the new actual and post-event refit.
- Move execution behind a main entry point and use a project-relative/configurable root as part of A07.

**Acceptance:** adding a previously unseen quarter succeeds without altering prior primitive observations; changing an existing consensus recomputes dependent surprise/sign; duplicate keys and inconsistent overrides fail; the prospective prediction is not overwritten by a refit using the new actual.

## 14. A12 — Model conventions requiring an explicit decision

These are not all confirmed arithmetic bugs. Do not make silent economic changes under the label “audit cleanup.”

### Valuation date alignment

`13_driver_model.py`, `valuation()`, seeds the DCF with FY2027 FCF, discounts the next annual flow one period, and adds FY2027 net cash/divides by FY2027 shares. This is naturally a forward valuation convention. Other football-field lenses use FY2027 or FY2028 exit metrics, while upside is calculated against the September 2026 spot. WS17 itself left valuation-date treatment open.

Choose whether the outputs are present fair values or forward targets. If forward targets, state target dates and return horizons and avoid calling them present discounted fair values. If present values, align cash-flow timing, interim flows, cash/share balances, and discounting. Do not average values at different dates without a defined convention.

### Share count after the arithmetic fix

The 597M starting count is explicitly sourced as **Q2 diluted weighted-average shares**, while the roll-forward calls its output period-end diluted shares. The WS18 correction removes double-counting but does not transform the anchor into an actual point-in-time fully diluted capitalization. In addition, applying a share price to SBC dollars is an issuance proxy, not a share-award schedule.

Document the approximation or build a more precise bridge. Distinguish period-end valuation shares from weighted-average EPS shares; the workbook appropriately calls net-income divided by its modeled shares an earnings proxy. Do not claim that proxy exactly reproduces reported GAAP EPS.

### Historical cash bridge and inert controls

Some FY2025 cash-bridge values are sourced estimates/reconciliation residuals, not independently disclosed actual lines. The FY2025 interest-expense memo is zero because of the bridge's classification, not proof of no borrowing expense. Keep source classifications clear.

The DCF-years input is now documented as layout-fixed. If it remains editable but inert, retain that warning; if advertised as functional, implement a dynamic strip and revalidate. Applying the same annual regulatory growth drag to each quarter is not automatically four times the annual effect; assess weighted annual aggregation before alleging a fourfold bug.

## 15. A13 — Make audit failures machine-detectable

`OVERNIGHT/analysis/src/overnight/17_excel_audit.py` and `17_scenario_switch.py` count/print mismatches and write reports, but do not reliably return a failing exit status when comparisons fail. A successful process exit therefore is not equivalent to a passing model audit.

**Repair:** preserve detailed reports but return a nonzero status for material reconciliation failures, missing required cells, or failed scenario comparisons. Keep informational static-scan findings separate from true validation failures; hundreds of raw pattern differences are not hundreds of defects.

**Acceptance:** a deliberately altered required output causes a failing exit code and a precise report; the clean workbook passes; legitimate tiny near-zero reconciliation residuals use a justified absolute tolerance alongside relative tolerance. Keep quoted rounded CSV values out of a full-precision comparison.

## 16. Resolved findings and corrections not to undo

### R01: FY2026 share-count double-counting is fixed in current OVERNIGHT

The original implementation started from the Q2 count but consumed FY2026 buyback and SBC flows. The repaired Python code now subtracts H1 buybacks and SBC for the FY2026 share roll. Excel now references the H1 anchors in the same way. `SHARE_ROLL_NETS_1H26 = True` is present.

Relevant current files:

- `OVERNIGHT/analysis/src/overnight/13_driver_model.py`, approximately lines 466–475.
- `OVERNIGHT/analysis/src/overnight/13_excel_builder.py`, approximately lines 775–784.
- `OVERNIGHT/data/processed/overnight/18_share_fix_delta.csv`.
- `OVERNIGHT/data/processed/overnight/18_corrections_applied.csv`.

The follow-up audit independently reran the pure Python mirror in memory and matched **all 216 named outputs** against the saved Excel comparison. Current base modeled share counts are approximately **588.850M in FY2026, 574.598M in FY2027, and 561.534M in FY2028**. The base football-field mean moved from approximately $162.65 to $160.22. Old WS17 prose contains pre-fix values; use the current model and WS18 delta ledger for exact scenario labels.

**Do not “fix” the current overnight share roll a second time.** MAIN's older model remains a version-consolidation issue under A07. The residual weighted-average-versus-period-end convention is A12, not a recurrence of the original arithmetic bug.

### R02: Workbook mechanics and synthesis integration improved

- The scenario selector now drives explicit Active columns on Valuation and Card_5Nov.
- Scenario-grid calculations read their axis cells.
- Historical anchors have source notes; FY2028 FX input units are clarified.
- Reverse-DCF solved inputs have a live staleness check.
- `research/notes/overnight/17_excel-audit.md` now exists.
- The WS18 ledger and current synthesis record application of WS16 corrections. The original audit's statement that these were pending is superseded for OVERNIGHT.

The current workbook contains **2,349 formulas**. The saved refreshed formula comparison reports **2,349 passes**. The scenario report has **143 rows, of which 141 are actual passing comparisons and two are change-count summaries**. Do not quote 143 as 143 numerical comparisons. The author of this handoff independently reproduced the 216 Python outputs, but did not independently run native Excel; the native recalculation evidence is the other session's saved dump/reports.

### Source correction: single service fee coverage

Do not repeat the old red-team allegation that roughly half of active listings on the single service fee was invented. The audit inspected `OVERNIGHT/data/raw/regulatory/transcripts/2026-Q2.txt` around line 272 and confirmed the statement is in the call transcript. It was absent from the shareholder letter, which is a different claim. WS16 correctly withdrew that allegation.

The direct-booking pilot's modeled 0–15bp take-rate impact is still an assumption/sensitivity, not measured adoption-based realized drag. Sourcing the fee terms does not empirically establish the proportion of GBV that will use the pilot.

## 17. Evidence limits and smaller cleanup items

- “Not found in public previews” must not become “does not exist.” WS16's inability to locate a current nights consensus or published options preview does not prove vendors have no estimates or that options contain no event information. No external re-verification of vendor availability was performed for this handoff.
- Consensus vendors differ materially on some prints; one cited nights comparison differs by roughly 2%. Preserve vendor/vintage metadata and test sensitivity to vendor changes. Do not silently splice them into a homogeneous series.
- The 9-of-9 guide-below-Street negative-return observation is exploratory. Its quoted base-rate-adjusted p-value is about 0.057, much less decisive than the unadjusted 0.0020 headline. It also inherits the event-return timing questions in A02.
- Treat the reported absence of a current fixed Inside Airbnb predictive panel as a sample/coverage limitation, not a reason to manufacture observations.
- MAIN's ex-SBC history has 20 quarters, whereas the later margin/capital-return work has 22; early missing quarters and the noted roughly $36M Q4 2023 identity gap deserve reconciliation when consolidating histories. The audit did not establish a new causal explanation for that gap.
- Some README counts are stale (for example database source counts), and WS17/WS18 notes contain historical states. Fix metadata without erasing dated provenance or rewriting history as though the final state existed throughout.
- The `ABNB-Crossover` tools are explicitly reference templates adapted from another workflow. Their presence is not proof of a functioning ABNB pipeline, but their deliberate template status is not itself a runtime defect that warrants rewriting every template.
- Regulatory exposure scenarios are not calibrated probabilities of stock moves. Matching licence IDs to observed listings improves exposure sizing, but calendar availability and modeled occupancy are not observed bookings or realized net revenue.

## 18. Suggested repair order and completion criteria

### Pass 1: protect the evidence base

1. Select the authoritative checkout and record its HEAD; check for concurrent edits.
2. Fix A01 leakage and A05 calendar alignment before rerunning research.
3. Fix A04 coverage eligibility, retaining both retrospective and cutoff-specific quality flags if needed.
4. Fix A09 CSV serialization and A11 append/derived-field logic.
5. Regenerate affected intermediate tables with input/output provenance and a clear old-versus-new delta.

### Pass 2: establish honest predictive validation

6. Implement A02's two separate timing tasks and A03's frozen temporal evaluation.
7. Save one row per historical forecast with all cutoffs, inputs, baseline, prediction, actual, and eligible return window.
8. Report incremental errors, sample sizes, uncertainty, and sensitivity on identical events.
9. Freeze the next-print prediction specification before observing the result. A future actual appended to a refitted dataset is not by itself a prospective test.

### Pass 3: repair model/risk interpretation

10. Fix A06's probability graph and rerun exposure/model overlays.
11. Fix A10's Excel boundary handling; decide A12 valuation/share conventions explicitly.
12. Resolve A08's event-variance identification or downgrade its output to an accurately labelled descriptive options measure.
13. Preserve R01/R02 fixes and ensure stale MAIN artifacts cannot be mistaken for current outputs.

### Pass 4: make the result reviewable and repeatable

14. Complete A07's build/dependency contract and A13's machine-detectable checks.
15. Rerun Python, workbook/native Excel, scenario-switch, and data-integrity validations appropriate to the changed files.
16. Update the synthesis, assumptions, figures, and forecast card from the corrected canonical outputs. Include a change ledger with numerical effects and remaining caveats.

**Ready for research handoff** means the confirmed implementation defects are corrected or affected outputs are explicitly excluded, the canonical build is repeatable, and the full temporal forecasting experiment is documented. **Ready to claim predictive alpha** requires additional evidence from that experiment; finishing code repairs alone does not meet that standard.

## 19. Audit coverage and verification record

The original audit included inventory and format checks across all observed uncommitted files, detailed review of active analysis code and relevant dependencies, data/output checks, and inspection of all 18 new figures. It did not independently re-read every external article or legally verify each regulatory assertion.

Verified during the original audit:

- 35 changed/untracked Python files parsed; both JavaScript modules passed syntax checks.
- 30 JSON files parsed. CSV checks covered 63 files across the two dirty worktrees; the two malformed rows were isolated to the one WS16 news CSV.
- SQLite integrity and foreign-key checks passed; selected table counts and matched regulatory cohort counts reconciled.
- Archived transcript hashes and 20 regulatory listing-snapshot hashes checked against manifests.
- Ten regression R² values reproduced independently from saved inputs.
- Twenty-six regulatory scenario revenue identities and selected spreadsheet outputs reconciled to their source data.
- Hawaii monthly/YTD occupancy identities checked; documented monthly-versus-YTD source differences were not mistaken for an undisclosed arithmetic fix.
- Workbook/archive ZIP integrity checks passed.
- The original 216-output Python/Excel comparison reproduced; the current WS18 216-output comparison was independently rechecked again for this handoff.

Important limitations:

- No repair source code, input data, workbook, or existing note was edited by this audit author. This handoff is the only authored file.
- External data acquisition was not rerun. Missing environment dependencies prevented a clean end-to-end replay of every pipeline.
- Native Excel was not independently controlled by the audit author. Saved native-Excel evidence was reviewed and the pure Python mirror was independently executed in memory.
- The custom evaluator and Python model share assumptions. Agreement is strong evidence of implementation consistency but cannot validate a common conceptual mistake.
- File/line numbers are reference anchors from this snapshot and may move. Search for the cited functions/expressions and verify current HEAD/status before editing.

## 20. Minimal commands for the next AI's initial orientation

These are read-only orientation commands, not a substitute for the acceptance checks above:

```powershell
git worktree list --porcelain
git status --short
git -c safe.directory=C:/Users/krish/citadel-abnb-overnight -C C:/Users/krish/citadel-abnb-overnight status --short
git -c safe.directory=C:/Users/krish/citadel-abnb-overnight -C C:/Users/krish/citadel-abnb-overnight log -3 --oneline
```

Start by reading `OVERNIGHT/data/processed/overnight/18_corrections_applied.csv`, the current model source, and this document's resolved section. Then verify open expressions against HEAD. Avoid importing research scripts blindly: some create directories or write outputs at module import time, and WS16 executes its merge/rerun at module scope.
