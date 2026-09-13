# Lane 1 full — verified closeout (v2)

The corrected lane is implemented and verified. **15 refuters made 112 explicit attacks. Four exact sentences (A, B, V, X) survived 3/3; R received 0/3 and is excluded.** This file supersedes the failed-run closeout. The failed v1 evidence remains preserved; all kernel-dependent packages use the verified K0 v2.

Branch: `codex/lane1-full`; repository: [Kaenyne/Citadel-ABNB](https://github.com/Kaenyne/Citadel-ABNB); base `b1dcdf91f77156b4cdbcf9a334db9b04cab30135` (merged PR #48).

## Package acceptance and results

All pass lines were recorded before their package results. The operational gates distinguish working software from evidence of an investment effect. Token usage is unavailable for every package and refuter; no estimate is represented as actual usage.

| Package | Pre-registered pass line | Result | Vintage / power / mechanism | Tokens |
|---|---|---|---|---|
| K0 | All 12 reference rounding intervals; specified six Q3/Q4 displays to 2dp; strict same-day/future/undated refusal in all six public functions; regional interface; module tests green; CLI <60s | **pass**: 12/12, 63 tests, 5.38s; default EWM; historical pre-guide abstentions retained | N/A: parent Gate 1, no three-refuter requirement | unavailable |
| A | At least 70% sign hits for strict abs(S)>1pp cells and positive signed executable next-open 20-day mean in both windows; n<6 is underpowered; Wilson 95% | **underpowered**: 0/14 W1, 0/10 W2; hit rate, Wilson interval and return effect undefined at n=0; 12 tests | survived / survived / survived | unavailable |
| B′ | At least 70% FY-revision sign hits where abs(T/FY midpoint)>0.5%, correlation >0.4 in both windows | **underpowered**: 0/14, 0/10 eligible FY-revision pairs; Q4/Q1 scenario only; 6 tests | survived / survived / survived | unavailable |
| V | Every figure traceable; supplied growth/change slope reproduced within its interval; one-screen page; independently checked vintages before any PIT claim | **partial**: final-model EBITDA lens $180.88 versus six-lens mean $156.79 reproduce; 6 tests; supporting W1 regression uses an undisclosed sample filter and is not admitted as stated | survived / survived / survived | unavailable |
| D | Fixed lambda/backlog/funds-payable card rows with source, owner, band and deterministic score rule | **partial**: 2/5 rows publication-scoreable; six integer-boundary cases independently checked; no parameters fitted | N/A: parent card check, no three-refuter requirement | unavailable |
| R | 72/72 revenue cells; every annual ADR attribution residual <0.8pp; regional ADR identified within ±10%; arrivals improve matched PIT errors in both windows | **partial**: 72/72 identities; 2024 residual −1.3943pp; maximum conditional ADR halfwidth 25.69%; no arrivals admitted at 0/14, 0/10; 7 tests after one registration correction | partial / partial / partial | unavailable |
| C3 | Beat the required RNPL-corrected ledger GBV baseline on both windows with stable coefficient sign | **underpowered**: required comparator 0/14, 0/10; no promotions; raw-ledger common n=3 in both windows is vacuous; 7 tests | N/A: parent pass-line check, no three-refuter requirement | unavailable |
| X | Annual ratios reproduce; regional quarterly revenue sums within 0.3%; independently measured dated O-D weights move gross scale toward disclosed non-USD share with interval; aligned Q3 FX comparison and both windows | **underpowered**: 24 annual ratios, 72 regional identities and 18 sums; zero measured Airbnb O-D currency cells; 0/14, 0/10 PIT origins; 19 tests | survived / survived / survived | unavailable |

The A/B magnitude thresholds above use abs notation; definitions are unchanged from the package notes.

## Gate evidence and reproduction

Full 0b output, exact initial branch/commit, network checks, and checkpoint history: [LANE1_RUN_LOG_v2.md](https://github.com/Kaenyne/Citadel-ABNB/blob/codex/lane1-full/docs/revenue-forecast-strategy/05_backtests/LANE1_RUN_LOG_v2.md). All 39 required paths existed. Initial harness/L0: **47 passed**; original kernel: **acceptance test: PASS on all 12 cells**. Loader: 25 calendar rows, 25 target rows, 13 registry methods, 161 vintage rows, 72 exact regional cells; LSEG 6 August Q3 value **4610.0**. FRED/NTTO/Eurostat HTTP 200 and yfinance succeeded; Rscript absent.

Gate 1: [K0_KERNEL_ENGINE_v2.md](https://github.com/Kaenyne/Citadel-ABNB/blob/codex/lane1-full/docs/revenue-forecast-strategy/05_backtests/K0_KERNEL_ENGINE_v2.md), [full receipt](https://github.com/Kaenyne/Citadel-ABNB/blob/codex/lane1-full/data/processed/forecast_methods/kernel_engine_v2/verification.txt). Q3 lambda 17.390785 / 17.145482 / 17.181818; Q4 11.946140 / 12.117264 / 12.025974. Displays: **17.39 / 17.15 / 17.18; 11.95 / 12.12 / 12.03**. Published three-decimal references use ±0.0005pp tolerance, avoiding double rounding. The 63 passing tests include refusal boundaries, regional dollar aggregation and provenance. CLI exit 0 in 5.384s.

Gate 2: [ALPHA_A_GUIDE_SURPRISE.md](https://github.com/Kaenyne/Citadel-ABNB/blob/codex/lane1-full/docs/revenue-forecast-strategy/05_backtests/ALPHA_A_GUIDE_SURPRISE.md). Parent verified the pre-result pass line, first-paragraph underpowered verdict, both window denominators, undefined n=0 Wilson intervals, vendor/timestamp coverage and exclusions, and executable-open-only return policy. K0 v2 is imported, lambda is not re-derived. No September consensus was placed at a historical origin. The gate passed as a clean negative with no A send-back.

Run from the repo root using its `.venv` Python:

```text
python -X utf8 -m pytest analysis/src/forecast_methods/harness/tests analysis/src/forecast_methods/L0 -q
python -X utf8 -m pytest analysis/src/forecast_methods/kernel_engine_v2/tests -q
python -X utf8 analysis/src/forecast_methods/kernel_engine_v2/run.py
python -X utf8 analysis/src/forecast_methods/alpha_a/run.py
python -X utf8 analysis/src/forecast_methods/alpha_b/run.py
python -X utf8 analysis/src/forecast_methods/valuation_v1/run.py
python -X utf8 analysis/src/forecast_methods/l1_reconciliation_v3/run.py --bootstrap 40
python -X utf8 analysis/src/forecast_methods/gbv_features_v1/run.py
python -X utf8 analysis/src/forecast_methods/regional_kernel_v1/run.py
```

Each package has its own README and local outputs. Default rebuilds use committed public extracts; optional public-refresh commands are documented separately. D is an addendum, not a model. The abandoned `kernel_engine_v1` remains explicitly unvalidated; it is not a supported dependency and its archived failure is not described as passing. This closeout does not claim that an unrestricted whole-repository pytest invocation passes. Across the supported packages, **120 tests passed**; the final frozen harness/L0 check passed **47/47** in 1.98s. The corrected R default runner was also rebuilt after its registration fix: **exit 0, 90.78s, 40/40 fits**, seven numerical tables unchanged, zero shared R registry writes. [Execution receipts](https://github.com/Kaenyne/Citadel-ABNB/blob/codex/lane1-full/data/processed/forecast_methods/lane1_control_v2/close-verification/test_receipt.json), [R full rebuild](https://github.com/Kaenyne/Citadel-ABNB/blob/codex/lane1-full/data/processed/forecast_methods/lane1_control_v2/close-verification/r_full_rebuild_receipt.json).

## Scorer and registry

The unchanged frozen scorer ran after all 15 refuters and the last registry correction in a byte-identical temporary repository copy, preserving frozen outputs. [Final comparison](https://github.com/Kaenyne/Citadel-ABNB/blob/codex/lane1-full/data/processed/forecast_methods/lane1_control_v2/after-refuters/comparison.json): exit 0, 10.84s, 4,109 registry rows / 69 objects / 276 score groups. All 366 source hashes and all 276 score rows match the before-A checkpoint. No leaders changed, so no SCOREBOARD_v3 is created. Existing PIT-labelled revenue leaders remain W1 optimal-mix/parsimonious (RMSE 33.884250, n=14), W2 optimal-mix/all (33.922215, n=10). Those frozen same-day conventions are not this lane's strict pre-guide alpha test.

No new method earned a valid historical registration. Unsupported live price, annual-gap and reconstruction dates were not forced into the frozen quarterly schema. R's one rejected attempt is retained only in `UNREGISTERED_rejected_registry_20260913`, with byte hashes; the shared registry contains none of those rows. Its corrected runner produces local candidates with actual UTC creation time. All 12 candidate values and 19 analytical files were unchanged. Empty ratios: **no baseline exists**. Same-ten-quarter apparent W1/W2 replications: **vacuous**. C3's common three-quarter diagnostic is likewise vacuous.

## FX conclusion and limitations

X's regional scenarios preserve a positive FX tailwind fading into Q4: principal after-hedge Q3 **+3.4–3.8pp**, Q4 **+1.5–1.7pp**; regional ADR-pass-through sensitivity **+3.2–3.6pp / +1.0–1.1pp**. These are assumption sensitivities, not measured exposures or historical confidence intervals. **X has not established a replacement for B4; B4 is not superseded.** The exact X headline remains subject to its three refuters below.

Missing evidence is a completed negative result, not an invented value. The supplied historical reactions have no executable open_* returns; strict pre-guide signal inputs and archived consensus are insufficient; no measured Airbnb origin–destination currency matrix is identified. Modern NTTO/JNTO/Eurostat observations cannot be backdated. R integrates no arrivals series into a historical predictive coefficient; Australia/Brazil are unintegrated and monetary tourism receipts are not visitor counts. Rscript is absent: X verifies the R-engine data contract with Python, not native R execution. Regional bootstrap and anchor sensitivity bands are conditional on modelling choices. V's change coefficient does not independently establish an exit-multiple level or an adopted target. The team decisions remain open.

## Independent refutation and admitted claims

Only the following four exact sentences are admitted by the pre-registered 2-of-3 rule. All 15 reviews are complete; partial votes do not count as survived. The [refuter index](https://github.com/Kaenyne/Citadel-ABNB/blob/codex/lane1-full/data/processed/forecast_methods/lane1_control_v2/close-verification/refuters.json) records all 112 attacks, assignments, verdicts and note hashes.

### A — admitted, 3/3 survived

> The supplied Lane-1 data do not establish a pre-guide expectations edge: the strict point-in-time test has 0 eligible signals across 14 W1 and 10 W2 guide dates.

Number and windows: **0/14 W1, 0/10 W2**; Wilson interval, numerical power and return effect undefined at actual n=0. Evidence: [A note](https://github.com/Kaenyne/Citadel-ABNB/blob/codex/lane1-full/docs/revenue-forecast-strategy/05_backtests/ALPHA_A_GUIDE_SURPRISE.md), independently checked against `L0_vintage_register.csv` and earnings-reaction schema. Votes and attacks: [vintage](https://github.com/Kaenyne/Citadel-ABNB/blob/codex/lane1-full/docs/revenue-forecast-strategy/05_backtests/REFUTE_A_vintage.md) survived (7), [power](https://github.com/Kaenyne/Citadel-ABNB/blob/codex/lane1-full/docs/revenue-forecast-strategy/05_backtests/REFUTE_A_power.md) survived (8), [mechanism](https://github.com/Kaenyne/Citadel-ABNB/blob/codex/lane1-full/docs/revenue-forecast-strategy/05_backtests/REFUTE_A_mechanism.md) survived (7).

Caveat: strict means before the calendar guide date. Same-day-inclusive consensus sensitivity gives **13/14 and 9/10 consensus observations**, not complete eligible signals. Missing consensus alone forces an empty joint test for every model; this cannot identify or reject the kernel mechanism. W2 is nested in W1, not ten independent additional events.

### B′ — admitted, 3/3 survived

> At strict pre-guide dates, the supplied data yield zero eligible FY-guide-revision tests in W1 (0/14) and W2 (0/10), so the live kernel–consensus gap is a conditional scenario, not validated revision alpha.

Number and windows: **0/14 W1, 0/10 W2**, with undefined hit rate, Wilson interval and correlation at n=0. Evidence: [B note](https://github.com/Kaenyne/Citadel-ABNB/blob/codex/lane1-full/docs/revenue-forecast-strategy/05_backtests/ALPHA_B_TERM_STRUCTURE.md), FY guidance ledger and dated L0 register. Votes and attacks: [vintage](https://github.com/Kaenyne/Citadel-ABNB/blob/codex/lane1-full/docs/revenue-forecast-strategy/05_backtests/REFUTE_B_vintage.md) survived (7), [power](https://github.com/Kaenyne/Citadel-ABNB/blob/codex/lane1-full/docs/revenue-forecast-strategy/05_backtests/REFUTE_B_power.md) survived (7), [mechanism](https://github.com/Kaenyne/Citadel-ABNB/blob/codex/lane1-full/docs/revenue-forecast-strategy/05_backtests/REFUTE_B_mechanism.md) survived (7).

Caveat: the three FY2026 percentage buckets are not dollar midpoint guidance, and the 12 FY consensus records all postdate the scored origins. A separate qualitative study would need a new pass line. The independent **1.790491%** cushion explains almost all of the live Q4 revenue gap against the lower consensus anchors; one-date arithmetic is not kernel-specific revision evidence. Three referenced raw-letter HTML files are absent, so primary-letter verification was not performed; the exact sentence concerns the supplied ledger.

### X — admitted, 3/3 survived

> The regional FX reconstruction does not yet justify replacing B4: no measured Airbnb origin–destination currency matrix is identified, and the current reconstruction has 0/14 W1 and 0/10 W2 point-in-time guide observations.

Number and windows: **zero measured currency cells; 0/14 W1, 0/10 W2**. Evidence: [X note](https://github.com/Kaenyne/Citadel-ABNB/blob/codex/lane1-full/docs/revenue-forecast-strategy/05_backtests/X_REGIONAL_KERNEL_OD_FX.md), official-source extracts in `regional_kernel_v1/public_inputs.csv`, and dated guide ledger. Votes and attacks: [vintage](https://github.com/Kaenyne/Citadel-ABNB/blob/codex/lane1-full/docs/revenue-forecast-strategy/05_backtests/REFUTE_X_vintage.md) survived (7), [power](https://github.com/Kaenyne/Citadel-ABNB/blob/codex/lane1-full/docs/revenue-forecast-strategy/05_backtests/REFUTE_X_power.md) survived (8), [mechanism](https://github.com/Kaenyne/Citadel-ABNB/blob/codex/lane1-full/docs/revenue-forecast-strategy/05_backtests/REFUTE_X_mechanism.md) survived (9).

Caveat: tourism visitors, nationality and domestic/foreign platform nights are not Airbnb settlement-currency exposure. The actual source releases postdate the historical guides; reconstruction today alone would not invalidate an otherwise admissible replay. All displayed FX cases remain positive and fade into Q4, but translation choices alter levels and can flip a near-zero ex-FX residual. Normalizing the predictor can change its coefficient without changing predictions. **B4 remains unsuperseded; this is not proof that B4 is optimal.**

### V — admitted, 3/3 survived

> Using the final FY27 base model, 16.5x adjusted EBITDA implies a $180.88 12-month target, while the existing six-lens base football-field mean is $156.79; these are different valuation objects.

Number: independently rebuilt **$180.876286 → $180.88**, six-lens mean **$156.786845 → $156.79**. Evidence: [V note](https://github.com/Kaenyne/Citadel-ABNB/blob/codex/lane1-full/docs/revenue-forecast-strategy/05_backtests/V_VALUATION_RECONCILIATION.md), final `13_model_annual.csv`, `13_valuation_summary.csv` and updated `model/assumptions.md`. Votes and attacks: [vintage](https://github.com/Kaenyne/Citadel-ABNB/blob/codex/lane1-full/docs/revenue-forecast-strategy/05_backtests/REFUTE_V_vintage.md) survived (7), [power](https://github.com/Kaenyne/Citadel-ABNB/blob/codex/lane1-full/docs/revenue-forecast-strategy/05_backtests/REFUTE_V_power.md) survived (7), [mechanism](https://github.com/Kaenyne/Citadel-ABNB/blob/codex/lane1-full/docs/revenue-forecast-strategy/05_backtests/REFUTE_V_mechanism.md) survived (8).

W1/W2: **not applicable** to the exact deterministic model identity; zero independently vintage-verified historical price forecasts were scored. The six lenses are dependent formulas on one base scenario, not six validation observations. Caveat: “12-month” retains the supplied approximately September-2027 convention using FY27-end cash/shares; date-interpolated arithmetic is **$179.444873**. The stale convention CSV is superseded by the documented FY28 discount rule. This sentence adopts no target or trading direction, and the growth regression is not required for either price.

## Partial headline — not admitted

### R — original sentence excluded, 0/3 survived

Original proposed sentence, **not memo-ready**:

> The full-sample regional refresh matches all 72 filed revenue cells but leaves a 1.39pp gap in 2024 ex-FX ADR attribution, so its FY27 composition remains conditional.

[Vintage](https://github.com/Kaenyne/Citadel-ABNB/blob/codex/lane1-full/docs/revenue-forecast-strategy/05_backtests/REFUTE_R_vintage.md): **partial**, 7 attacks. [Power](https://github.com/Kaenyne/Citadel-ABNB/blob/codex/lane1-full/docs/revenue-forecast-strategy/05_backtests/REFUTE_R_power.md): **partial**, 8 attacks. [Mechanism](https://github.com/Kaenyne/Citadel-ABNB/blob/codex/lane1-full/docs/revenue-forecast-strategy/05_backtests/REFUTE_R_mechanism.md): **partial**, 8 attacks. The input contains **56 directly filed cells and 16 Q4 back-outs**, so “72 filed” overstates the direct-disclosure count. The refuters independently trace all 72 accounting inputs to filing sources, but their permitted note/raw-input scope does not independently reproduce the R fitted endpoint. Subtraction of reported endpoints **2.0457−3.44=−1.3943pp** verifies rounding, not the model estimate. No weaker replacement sentence is silently admitted.

Evidence: [R note](https://github.com/Kaenyne/Citadel-ABNB/blob/codex/lane1-full/docs/revenue-forecast-strategy/05_backtests/R_REGIONAL_REFRESH.md), `L0_exact_regional_revenue.csv`, original XBRL regional source, and preserved rejected registry files. W1/W2 contain **56/40 accounting target cells**, with **0/14 and 0/10** historically admissible current-arrivals origins. The reported bootstrap reuses 18 quarters; 40 refits are not 40 new observations. Conditionality remains warranted, but the original exact sentence did not receive the required independent support. The power review also cannot reconcile 118 raw included regional intervals to the reported 127 model constraints from the note's specification alone.

## Partial and refuted supporting interpretations

V's literal W1 regression specification does not reproduce its reported sample. The power refuter obtains 45 monthly changes and slope **0.505028** with HAC(12) interval **[0.356854,0.653202]**; the note's 35-change **0.486022** result appears only after excluding January–October 2023. Parent source inspection locates growth/margin filters applied before the 12-row difference (`valuation_v1/run.py`, lines 126–129), absent from the pre-result note. Parent inspection also confirms that level regressions use HAC(6), whereas the refuter's literal HAC(12) check yields different intervals; that lag choice was not disclosed beside the level table. These are retrospective diagnostics, not new adopted estimates. The reported growth-to-multiple relation does not qualify as a validated memo claim. The two deterministic valuation prices do not depend on that regression.

## RESUME

Use K0 v2 and the four exact admitted sentences with their stated caveats. R's original sentence and V's supporting statistical interpretation are not approved for memo use. Any future historical alpha test needs a new pre-registration and admissible dated inputs; do not repair missing observations or prior issuance with a format date. Preserve frozen files and previous failed evidence. The final publication result and elapsed-time accounting are recorded in LANE1_RUN_LOG_v2.md.
