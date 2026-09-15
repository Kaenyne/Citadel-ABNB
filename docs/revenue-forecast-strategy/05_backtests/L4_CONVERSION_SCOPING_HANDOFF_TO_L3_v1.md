# Conversion scoping handoff to L3

2026-09-13. L4 read-only scoping, preserved after the user's role correction. **L3 owns conversion estimation and validation. No new weight or seasonal coefficient was estimated, no conversion test ran, and no candidate specification was adopted by L4.** L4 resumes its revenue/guide, financial model and review artifacts with the existing fixed kernel as a provisional benchmark.

## User request for the separate L3 task

Preserve the existing 2/3-1/3 benchmark. In a new version estimate four seasonal conversion rates and one shared lag weight on all 22 lag-complete historical quarters. Validate separately using chronological refitting, matched W1/W2 comparisons, confidence intervals and sensitivity to individual years. Determine whether estimating the weight improves reliably; do not select solely on significance. Deliver the recommended specification, uncertainty, validation exhibit and exact presentation claims. Distinguish predictive coefficients from actual booking-to-recognition shares.

## Verified input inventory

`data/processed/overnight/02_kpi_panel_quarterly.csv` contains 24 consecutive source quarters, 2020Q3-2026Q2. Constructing both exact calendar lags leaves 22 target quarters, **2021Q1-2026Q2**: seasonal counts Q1=6, Q2=6, Q3=5, Q4=5. Use `gbv_musd`, not rounded `gbv_busd` multiplied by 1,000. The two 2020 seed quarters carry $8,029.3M and $5,905.7M of GBV. Choose and disclose the revenue field; do not silently mix letter and XBRL values.

Main-harness W1 contains targets 2023Q1-2026Q2 (14); W2 contains 2024Q1-2026Q2 (10). At the preceding-quarter letter close, prior target training counts are 8-21 for W1 and 12-21 for W2. Apply `docs/thesis-kernel-topdown/lane2/CONVENTION.md`: the just-issued letter is available at its date-only close. Published outcomes after that date must never train the fold.

Source hashes are preserved in `data/processed/forecast_methods/lane4_control_v1/baseline/tracked_hashes.json`. Starting committed input version: `1c87628cedbc94ab8a0e8552743c94485ef353b8`. The sample verification command was:

```powershell
python -c "import pandas as pd; p=pd.read_csv('data/processed/overnight/02_kpi_panel_quarterly.csv'); print(p[['quarter','revenue_musd','gbv_musd']].to_string(index=False))"
```

## Methodological issues for L3 to preregister

These are scoping suggestions, **not a finalized preregistration or new findings**.

- Isolate weight estimation by fitting free-weight and fixed-2/3 versions on identical samples with the same loss and season-calibration method. Show untouched K0 v2 as a separate deployed-policy benchmark. Dollar-SSE and relative-SSE answer different weighting questions; predeclare the primary objective and report both error scales.
- At fixed weight, seasonal coefficients can be solved analytically. For dollar-SSE, lambda_s=sum(B*R)/sum(B^2). For relative-SSE, a=B/R and lambda_s=sum(a)/sum(a^2). The mean of R/B is a different estimator. Do not inadvertently compare different loss functions and attribute their difference to the weight.
- Profile the shared weight over [0,1], include boundaries and check the global minimum. Positive revenue and GBV do not make significance of a positive lambda economically informative.
- Keep the full-22 fit descriptive. Fit every historical prediction chronologically. The first W1 fold has only eight targets for five parameters; report this limited information, season counts and any boundary solutions.
- K0 v2 owns its existing nested ex-COVID/last-three/EWM selection. Its fallback may abstain at early W1 origins with no eligible same-season observations. Report actual common coverage and missing origins; never fill or alter the frozen benchmark to force a comparison.
- Report profile flatness plus conditional parameter intervals from a preregistered bootstrap that preserves appropriate temporal blocks. Resample already-constructed rows with their genuine lag covariates; do not create fictitious historical lags by concatenating sampled quarters. State seed, draws, block choice, rejection rules, boundary mass and small-sample limitations. Parameter confidence intervals are distinct from predictive intervals.
- Leave out each calendar year 2021-2026 in turn and refit; 2026 has two target observations. Show parameter and forecast-level sensitivity. Four quarters within one year cannot separately identify five parameters.
- Match W1/W2 target rows for every pairwise comparison, score disclosed revenue integers as +/-$0.5M intervals, and report ordinary dollar/relative errors too. Predeclare a practical improvement hurdle and robustness requirements before running; do not adopt on significance alone.

## Interpretation constraints

The shared coefficient w is predictive, not a measured booking-to-stay probability. Under the assumed model the first-lag revenue-dollar contribution is proportional to `w * GBV_lag1`, and its share is `w*GBV_lag1 / (w*GBV_lag1+(1-w)*GBV_lag2)`. It generally differs from w. Lambda also absorbs omitted in-quarter bookings, fees, cancellations, FX, mix and the reported accounting basis. Recognition shares need separate cohort evidence.

The historical data file is a current cached history, not a complete archive of original vintages. The 2020Q3 calendar date is marked approximate in the existing spine. Post-letter forecasts with the preceding-quarter prints do not demonstrate advance knowledge of that same letter's already-announced guide.

Relevant prior notes: `kernel-lambda.md`, `K0_KERNEL_ENGINE_v2.md`, `K1_KERNEL_WEIGHTS_AND_BACKLOG.md`; source `kernel_phi_v2/phi_fit.py`. The K1 five-lag panel starts 2021Q3 with 20 targets and must not silently replace the requested 22-row sample. Older weight sweeps are different experiments and are not results or pass lines for this study.

## L4 consumption boundary

L4 awaits an explicitly accepted L3 version or commit with checksums, estimation policy, coefficients, uncertainty definitions, information dates, validation verdict and permitted claims. L4 will keep the fixed benchmark visible, replace the appropriate conversion component once if accepted, and rerun revenue/guide, financial and memo checks. No changing L3 worktree is consumed.

## RESUME

The user can carry this note to the separate task "Complete and audit L3." L3 should own and preregister the research choices before running. L4 should complete its provisional baseline package and leave conversion-dependent claims qualified until accepted L3 results arrive. No outreach or cross-task message was sent.
