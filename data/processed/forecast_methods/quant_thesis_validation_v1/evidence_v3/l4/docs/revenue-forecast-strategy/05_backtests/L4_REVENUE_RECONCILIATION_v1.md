# L4 — operating inputs, benchmark revenue and management guide

Codex reconciliation subagent · 13 September 2026 · `codex/lane4-full` · starting commit `1c87628cedbc94ab8a0e8552743c94485ef353b8`. New package only: `analysis/src/forecast_methods/lane4_revenue_v1/`, matching processed-data folder and this note. Parent owns registration, scorers, workboard and publication. Methods/acceptance were fixed in `LANE4_PREREG_v1.md` before calculation.

## Verdict

**Implementation PASS; research integration PARTIAL.** The H2 v3 $3,059.403M Q4 guide and K0 $3,158.228M guide reconcile to less than $0.001M, with no unexplained overlay. Published ADRv3 dollar ADR times nights produces a review benchmark of **$3,179.344M Q4 revenue / $3,123.419M guide** using K0's fixed 2/3 conversion and trailing-eight median cushion. This is a conditional review object, not a signed forecast or evidence of an expectations edge. Conversion-dependent conclusions remain provisional pending accepted L3 conversion estimation/validation; cohort FX/RNPL integration is separately pending. No new conversion weight is estimated here.

The implementation has 36 passing tests; all 13 CSVs rebuild byte-identically; 17 source/code hashes pass independent verification. Missing L3 inputs remain null rather than zero. The model retains inherited reported-revenue accounting, including embedded translation and hedge effects. An after-hedge timing adjustment is refused without a verified hedge split.

## What ran

Commands from the isolated worktree root; this Windows environment uses the original workspace's existing interpreter:

```text
"C:\Users\wille\Desktop\Citadel - ABNB\.venv\Scripts\python.exe" -X utf8 -m pytest analysis/src/forecast_methods/lane4_revenue_v1/tests -q
"C:\Users\wille\Desktop\Citadel - ABNB\.venv\Scripts\python.exe" -X utf8 analysis/src/forecast_methods/lane4_revenue_v1/run.py
"C:\Users\wille\Desktop\Citadel - ABNB\.venv\Scripts\python.exe" -X utf8 analysis/src/forecast_methods/lane4_revenue_v1/run.py --output data/processed/forecast_methods/lane4_revenue_v1/rebuild_01
```

Final tests: exit 0, 36 passed in 1.86 seconds (shell wall 4.71 seconds). Final runner: exit 0, calculation wall 3.28 seconds (shell wall 4.41 seconds), completed `2026-09-13T23:25:02Z`. Rebuild: exit 0; 13/13 CSVs byte-identical. An intentional second default invocation returned exit 1, “Refusing existing output directory”; every existing output hash remained unchanged. Receipt: `data/processed/forecast_methods/lane4_revenue_v1/validation_receipt_v1.json`. Final immutable calculations are under `snapshot_v1/`; `rebuild_01/` is a separate reproduction.

The runner makes the calculation, reads all source inputs and writes their hashes. Tests independently check hand-calculated kernel/currency examples, conservation, zero/full RNPL, equal booking/recognition rates, currency direction, missing/future inputs, exact lag timing, denominator reconstruction, hashes and directory escape, duplicate application and positive/negative/zero hedge contributions. Separate Decimal arithmetic from the published card cells reproduces Q4 revenue $3,179.343654286M and guide $3,123.419115173M.

## Reconciled guide: what explains the $98.825M difference

All dollar values are USD millions. Each row is one deterministic Q4 comparison, n=1; none is a historical backtest. Sequential order is GBV, lambda, cushion, explicit overlays, information date. Interactions follow that fixed order.

| Step | n | Guide | Change |
|---|---:|---:|---:|
| H2 v3 original | 1 | 3,059.403011 | — |
| Q3 GBV $26,027.962983M → K0 $26,449.972322M | 1 | 3,091.983456 | +32.580444 |
| Lambda 12.029792635% → K0 EWM 12.040366938% | 1 | 3,094.701339 | +2.717883 |
| Cushion 3.88% → trailing-eight median 1.790491031% | 1 | 3,158.227962 | +63.526624 |
| Additional fee/FX/cancellation overlays absent on both dollar paths | 1 | 3,158.227962 | 0.000000 |
| September 12 → September 13 information roll; no new KPI print | 1 | 3,158.227962 | 0.000000 |

The final attribution residual is −4.55×10⁻¹³M. “Absent overlay” describes the legacy dollar equations; it does **not** mean economic FX is zero. H2 v3 uses the 2023–25 Q4 mean conversion and a 3.88% Q4 historical cushion. K0 imports its existing EWM selection and the most recent eight realized actual/guide ratios. Both calculations were available on September 12; current reported KPI inputs remain through the August 6 release. H2/ADR FX assumptions ultimately use the earlier September 4 FX inputs. Existing source outputs and code are preserved.

The review reference differs from H2 v3's rate-compounded GBV: **146.8m nights × $177.17 = $26,008.556M**, rather than $26,027.962983M. Using the explicit identity avoids stitching incompatible rounded source growth rates into the operating model. Printed historical GBV is retained as reported; independently rounded historical nights/ADR are not forced to recreate it.

## Review benchmark and comparisons

All rows below are current conditional objects, W1 n=0 / W2 n=0. No empirical confidence interval or scenario probability is supplied. Each value represents one forecast quarter; table n is the number of quarters in that row.

| Scenario | n | Q3 revenue | Q4 revenue | Q4 guide | Q1 2027 revenue | Q1 guide |
|---|---:|---:|---:|---:|---:|---:|
| Team Q3 nights + ADRv3 with K; Q4 case B | 3 | 4,808.363 | 3,179.344 | 3,123.419 | 3,055.681 | 3,001.931 |
| Same nights, ADRv3 without K | 3 | 4,808.363 | 3,175.926 | 3,120.062 | 3,046.829 | 2,993.235 |
| Q4 case A nights 132.7m replaces case B 131.8m | 3 | 4,808.363 | 3,179.344 | 3,123.419 | 3,069.012 | 3,015.028 |
| Residual mean-reversion sensitivity, K retained | 3 | 4,808.363 | 3,129.866 | 3,074.812 | 2,983.609 | 2,931.127 |
| Inherited K0 conditional GBV comparison | 3 | 4,808.363 | 3,214.776 | 3,158.228 | 3,121.423 | 3,066.517 |

ADRv3 published midpoint inputs are Q3 nights 146.8m and ADR $177.17 with K / $176.88 without; Q4 case B nights 131.8m and ADR $174.57 / $173.94. The with-K Q4 GBV input is $23,008.326M. K0 supplies GBV rather than a separate nights/ADR decomposition, so its two operating fields remain unavailable. Its undisclosed RNPL ramps and recursive GBV-growth persistence remain labelled conditional assumptions, not evidence for an RNPL share.

The fee comparison **replaces** the published without-K ADR with with-K ADR. It adds $3.417M of Q4 revenue / $3.357M of guide and $8.852M / $8.696M in Q1. It is not a second fee/take-rate overlay or a causal fee estimate. Mean reversion replaces only the last-quarter residual (4.849326pp) with the source's historical-mean 2.398pp; geographic mix, unit size, length of stay, seats/interaction fills and K stay unchanged. No extra cancellation or seat deduction is added.

### Timing and actual contribution weights

Each row below contains two lag cohorts, n=2. Kernel coefficients are fixed 2/3 and 1/3; contributions depend on each cohort's GBV.

| Revenue target | n | Lag-1 USD GBV | Lag-2 USD GBV | Actual USD contribution weights |
|---|---:|---:|---:|---|
| 2026Q3 | 2 | 27,200.000 | 29,200.000 | 65.0718% / 34.9282% |
| 2026Q4 | 2 | 26,008.556 | 27,200.000 | 65.6640% / 34.3360% |
| 2027Q1 | 2 | 23,008.326 | 26,008.556 | 63.8896% / 36.1104% |

Q3 contemporaneous nights/ADR have no effect on Q3 revenue under this benchmark. Q3 GBV affects Q4; Q4 GBV first affects Q1 2027. These are USD-baseline contribution weights, not measured booking-to-stay probabilities or the constant-reference currency weights L3 must supply.

### Issued guidance and cushion decisions

Q3 guidance was already issued August 6: $4,690–4,770M, midpoint $4,730M (n=1 event). The implied Q3 benchmark guide $4,723.784M is a diagnostic, not a future guide forecast. Multiplying the actual midpoint by the current median cushion gives revenue **$4,814.690M** (+$6.327M versus kernel); using the mean gives **$4,817.824M** (+$9.461M). Both cushion estimates use n=8 realized outcomes through August 6. The original Q3 method choice remains open.

For Q4 review GBV/lambda, median cushion gives guide $3,123.419M; mean 1.856743063% gives **$3,121.388M** (−$2.032M); the inherited Q4 3.88% gives **$3,060.593M** (−$62.826M). Each is one conditional Q4 sensitivity, n=1, not an estimated distribution. Relative ±1% changes to Q3/Q4 nights and ADR are separately tabulated with timing respected.

### Vendor-stamped comparisons

One Q4 guide compared with each latest admissible family observation (n=1 vintage each). Yahoo and Alpha Vantage count as one LSEG-family panel; no vendor-average forecast is constructed.

| Vendor | Analyst n | Observation attached to value | Consensus | Guide gap | Gap % |
|---|---:|---|---:|---:|---:|
| Yahoo Finance / LSEG family | 36 | 2026-09-13 15:20 UTC | 3,161.02149 | −37.60237 | −1.18956% |
| S&P Global via StockAnalysis | 35 | 2026-09-10; time not recorded | 3,160.00000 | −36.58088 | −1.15762% |
| Zacks | 10 | 2026-09-11; time not recorded | 3,200.00000 | −76.58088 | −2.39315% |

The S&P and Zacks rows are older existing anchors, not refreshed observations. Capture date is not automatically a new vendor-publication date or a consensus revision. URLs, register IDs, units, timestamps and source paths accompany every comparison in the output. This arithmetic alone does not establish that management will disappoint expectations.

## L3 integration and accounting limits

Two dependencies remain open: L3 conversion estimation/validation and L3 cohort FX/RNPL inputs. Neither is silently consumed from a changing worktree. Current `conversion_status` explicitly calls fixed K0 a provisional benchmark. `fx_integration_status` is pending; incremental FX, hedge dollars and FX-neutral revenue are null. The external R bundle was consulted as a read-only interface reference; no synthetic example numbers were imported and no bundle file was copied or staged by this agent.

The implemented FX adapter requires an explicit version/commit, file checksums, target/scenario, units, source/date, evidence status and incremental-versus-replacement treatment. Parent must additionally verify the file contents against the claimed Git commit: a 40-character string and matching local hashes alone do not prove that lineage. Fixed coefficients times supplied reference-currency GBV produce w; each cohort's currency-specific booking and recognition ratios preserve units. Both reference-currency lag totals must reconstruct the exact baseline USD GBV. RNPL stays in total bookings. Stock-derived unpaid shares and booking-flow shares are rejected as recognized-revenue weights.

Recognition-period FX is a working hypothesis, not an accounting fact. At the quarterly interface, a target-quarter revenue allocation must use that recognition quarter; other payment/fixing-date hypotheses require a separately named specification. Missing rates are refused even in a zero-RNPL fixture. A supplied multiplier must equal the incremental ratio F_retimed/F_booking, rather than adding the full FX factor to already translated USD GBV.

After-hedge application requires explicitly verified baseline hedge dollars h and computes **(R−h)×multiplier+h**. This preserves positive or negative hedge dollars. Missing h is not replaced by zero. Management's stated after-hedge YoY FX contribution, an economic translation level multiplier and a change in YoY contribution are separate quantities; none is automatically an additive adjustment here. The contract prevents applying a timing adjustment twice. More complex accepted L3 conversion or timing specifications require a new version rather than modifying this benchmark silently.

## Failures, parameters and honest interpretation

Development run 01 failed because the L0 field is `period`, not `target_period`; its `FAILED_RUN.json` is preserved. Runs 02/03 completed and remain as checkpoints. Final output refusal was an intentional successful safety check. No failed empirical test was discarded; no new empirical conversion test was run. The frozen scorers are parent-owned, so this package makes no assertion that registration or shared scoring has completed.

There are **zero newly fitted parameters**. Each target imports one K0 seasonal coefficient: Q3/Q4 use five same-season observations each, Q1 six. Across this package there are three queried seasonal coefficients; the inherited engine has four seasons, fixed lag 2/3, three candidate lambda estimators, a nested selection rule and an EWM half-life of two same-season observations. Cushion uses the eight most recent realized ratios. Nights, residual/K mechanics, scenarios and ±1% sensitivities are explicit assumptions, not statistical degrees of freedom disguised as measurements.

ADRv3's conditional dollar-target result uses windows n=10/n=9, distinct from the main harness. Its rule was selected after earlier analysis; the integer-fair ex-FX target did not pass both windows. The imposed K coefficient's small improvement does not identify causal pass-through. A2 remains PARTIAL without an established executable trading edge; B2 failed its revision-mechanism hurdle; RNPL migration remains unidentified. No failed regional/new-listing addition, withdrawn FX subtraction, fitted fee coefficient, scenario probability or adopted trade target is revived.

## Harness change requests

None. Parent may register genuinely new supported LIVE operating-scenario objects at the actual run date, with no invented quantiles and distinct scenario object names. Q3 is unchanged across the operating scenarios and should not be registered repeatedly as new information. No unavailable FX result is eligible for registration. Keep these benchmark comparisons provisional until L3 conversion work is accepted.

## RESUME

Parent should integrate `snapshot_v1/` into the workbook, exactly two-page memo, unsigned card and decision register, review both pending statuses, verify the package source/output hashes, and run the required registration/scorer checks under its own ownership. Numerical outputs are stable; the independent receipt includes byte-identical rebuild and refusal checks. When the user manually provides L3's versioned conversion and cohort-FX handoffs, verify commit contents and checksums, assess the evidence and baseline/hedge compatibility, then rebuild affected results in a new version. Do not promote fixed K0 conversion, RNPL timing or any investment decision merely because this implementation passes its accounting tests.
