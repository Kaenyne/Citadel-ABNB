# GE delivery — conversion, uncertainty and earnings entry

15 September2026. Parent agent; subagents roadmap_auditor (forecast and independent review), chart_auditor (events), source_auditor (sources and memo). Preregistered audit: GE_PREREG_v1.md. Ownership: SR_GBV_CONVERSION_TRACK_SCOPE_v2.md. This completes the available-data audit and artifacts, not proof of an investable short.

## Four-quarter model

We preserve Bq=(2/3)GBVq-1+(1/3)GBVq-2, revenue=lambda*Bq, guide=revenue/(1+cushion). Lambda is an empirical conversion ratio, not take rate; Bq is not guaranteed backlog and the weights are not physical booking shares. Four inherited seasonal EWM parameters plus one trailing-eight median cushion: five estimated path scalars, zero newly optimized parameters. Seasonal n=5/5/6/6 and cushion n=8 are separate training counts, not independent observations to add together.

| Target | Weighted GBV $m | Revenue $m | Guide $m | Interpretation |
|---|---:|---:|---:|---|
|2026Q3|27,866.667|4,808.363|4,723.784|Diagnostic only; already-issued observed guide midpoint4,730 |
|2026Q4|26,405.704|3,179.344|3,123.419|Conditional future guide |
|2027Q1|24,008.403|3,055.681|3,001.931|Conditional future guide |
|2027Q2|29,285.681|4,048.395|3,977.184|Explicit Q1 GBV input32,424.358; no inherited revenue-growth fallback |

Canonical integration is `data/processed/forecast_methods/gbv_event_v1/integration_v2/`. It preserves the prior three-quarter working outputs within1e-7, makes Q2 explicit and binds transitive KPI/calendar/cushion sources. Review removed a historical pre-guide LSEG row from the current comparison set and renamed the conditional break-even conversion. Q1 actual availability is correctly dated7May, not the common August cutoff. Exact filing GBV29,187/27,247 is a separately labeled frozen precision comparison; no silent parameter refit.

Yahoo/LSEG-family quarterly revenue estimates observed13September give Q3=4,744.88187 and Q4=3,161.02149. With the same1.790491% cushion, Q4 Street guide proxy=3,105.419237; our gap=17.999878 (+0.579628%). The direct guide expectation is not observed. Comparing our guide3,123 with revenue consensus3,161 would create an invalid bearish comparison. The sign differs against the coarser Zacks proxy; no panel is silently substituted. Q1/Q2 quarterly Street values remain unavailable.

Holding other inputs fixed, revenue parity is reached at Q3 GBV25,780.296790 (-0.877631% from the working assumption) or Q4 lambda11.970980% (-6.938715bp). These are conditional boundaries, not probabilistic short triggers. Shared-cushion relative guide disagreement algebraically equals revenue disagreement. Excel permits the expectation cushion to be edited separately; changing only our cushion holds that benchmark fixed.

The GBV assumptions still inherit the prior working case, with component-derived ancestry shared with Krishang; that is not independent confirmation. RNPL cancellation/timing risk needs a measured incremental change in GBV/conversion/cushion. No second haircut or FX factor was added.

## Quant results and failures

| Fixed earlier-origin guide test | W1 n12 | W2 n10 |
|---|---:|---:|
| Candidate RMSE, midpoint +/-0.5m |63.4447|63.6962|
| Guide-growth baseline, same rows |74.3308|60.8344|
| Revenue-naive/cushion baseline, same rows |117.3090|121.9259|
| Candidate raw RMSE |63.8562|64.0989|
| Actual-GBV oracle raw RMSE |36.3730|38.6966|

Promotion fails: the candidate loses to the guide-growth baseline in W2 and fails deletion stability. The oracle substitutes future realized GBV and is not tradable. The replay is the frozen ex-COVID earlier-origin candidate; the current four-quarter working case uses inherited EWM conversion. These statistics identify method risks, not a direct backtest of this exact EWM case or calibrated long-horizon probability bands. Twenty prior CSVs were reproduced;617 strict input-date checks and future-input poisoning at21 origins passed. Historical origins were approximately48–62days before guidance. Two events contribute51.34%/61.14% of squared error.

W1 raw guide-error population variance4,027.252 USDm squared comprises diagonal factor variance6,825.525 plus covariance contribution-2,798.273. W2 corresponding figures4,097.019=7,759.693-3,662.674. Shapley attribution is a symmetric accounting decomposition, not causality. Assuming independent factors would materially misstate aggregate uncertainty.

The full23-event panel has20 numeric first guides,16 attributed original revenue-consensus proxies and15 prior-cushion adjusted proxies. For the original full-sample proxy, Pearson r is0.324 for QQQ-excess gap and0.310 for next-session excess return. Gap slope1.117pp per1pp proxy has approximate95% CI[-0.966,3.200]; session slope0.514 has CI[-0.294,1.321]. All12 primary Holm-adjusted p-values are1.0. Neither the observed relationship nor early-origin sensitivity establishes a stable net-of-cost trading edge. W1/W2 event-print counts are distinct from the forecast-target12/10 sample. Adjusted proxies have no negative sign examples; they cannot support a calibrated downside response.

Daily gap includes release, call, overnight and premarket news. It is not a call-only return. A published guide cannot be used as a pre-release signal to earn that gap. Pre-event entry requires the whole origin-to-exit exposure; next-open entry can earn only subsequent returns. Held daily OHLC cannot recover wick order or stops, and there are zero verified intraday call panels. The expected5November date is planning information, not issuer confirmation from this audit.

## Deliverables and verification

`outputs/gbv-event-20260915/ABNB_GBV_guidance.xlsx`: seven sheets, seven native charts, four-quarter formulas, explicit inputs and source dates, missing/zero guards, GBV/lambda sensitivity, covariance diagnostics, full23-event price legs, trade-entry distinctions and source lineage. Historical audit tables and the input-precision comparison are frozen references. The decision wording updates with the guide gap. Direct expectation cells remain blank until a sourced value is supplied.

`output/pdf/gbv-event-20260915/ABNB_GBV_two_pager.pdf`: exactly two pages, three charts, editable same-name Markdown companion. Both pages were rendered and independently inspected. It is a completed analytical research memo with a conditional conclusion; no submission or trade was executed and competition-format acceptance was not independently certified.

Artifact-tool recomputation and input perturbations passed; formula scan matched zero errors. The final workbook was then opened in a separate hidden Microsoft Excel16.0 instance. Full rebuild, guide/gap tie-outs, observed Q3 treatment, GBV propagation, zero/missing cushion, fixed expectation benchmark and restoration passed. Excel refreshed all seven charts and saved the final file. See native_excel_checks.json and the exact final OOXML independent review.

The bundled PNG renderer hit native Windows teardown0xC0000409 after completing saves; explicit JS termination did not fix it. Default author/export now excludes optional rendering and exits0. Existing previews were reviewed; Excel native validation closes the calculation/export boundary. The first sandboxed Excel attempt could not access the Windows logon session (COM0x80070520); scoped approved execution succeeded. No denial or unresolved permission block remains. These failures are retained here rather than mislabeled as successful executions.

Seven new FORMAT1.1 LIVE PIT records (4revenue,3futureguide, real vintage15September) are point-only, with q50=point required by the schema and no calibrated distribution claim. Both unchanged scorers ran before and after with output paths redirected to new audit folders. All288 historical rows match across versions and before/after.120 pre-existing files were preserved; existing checked-in scoreboard drift is documented separately in GE_REGISTRY_SCORING_v1.md. No frozen scoreboard was overwritten.

## Exact commands

Commands ran from the submission-readiness worktree root; the bundled Python and Node runtime binaries were used. Each research runner's README gives its complete arguments and fresh-output guard.

```powershell
python analysis/src/forecast_methods/gbv_event_v1/integration/run.py --out data/processed/forecast_methods/gbv_event_v1/integration_v2
python -m unittest discover -s analysis/src/forecast_methods/gbv_event_v1/integration -p test_integration.py -q
python analysis/src/forecast_methods/gbv_event_v1/artifacts/stage.py --events run_v3
node analysis/src/forecast_methods/gbv_event_v1/artifacts/build.mjs
& ./analysis/src/forecast_methods/gbv_event_v1/artifacts/verify_excel.ps1
```

Integration4 tests pass. Forecast original13 + additive10 tests pass. Event12 tests pass. Registry5 tests pass. Independent source314 and event2,004 arithmetic/selection checks pass. Final artifact review binds workbook formulas, cached values, native charts and exact hashes; PDF QA receipt binds the two-page file. No existing tracked file was changed, and no commit/push/PR was created in this delivery turn.

## RESUME

Use this workbook and memo as the four-quarter conditional research baseline. First strengthen future GBV inputs and obtain timely, vendor-dated expectations of the actual guidance object; do not force a short from the current positive Yahoo comparison or substitute a favorable panel. If promoting the current EWM path, pre-register its exact earlier-origin replay and require both-window/deletion survival; historical ex-COVID diagnostics are not that proof. If pursuing a during-call trade, acquire consistently timestamped ABNB/QQQ bars and exact release/call boundaries, then pre-register executable entry/exit and cost assumptions. A failed edge test remains a result. Keep scope through Q2 2027 and preserve the component/cost track as a separate owner.
