# Conversion validation v1

Five-parameter research specification: four seasonal through-origin conversion rates and one common bounded lag coefficient. This package audits the 22-quarter descriptive fit separately from prospective weight promotion and production adoption. The existing operational fixed kernel remains unchanged.

From the repository root (numpy, pandas, scipy, matplotlib, statsmodels and pytest required):

```powershell
python -B -m pytest analysis/src/forecast_methods/conversion_validation_v1/test_conversion.py -q -p no:cacheprovider
python -B analysis/src/forecast_methods/conversion_validation_v1/run.py --out data/processed/forecast_methods/conversion_validation_v1/results_NEW_VERSION
```

Every output directory must be new. Replace `NEW_VERSION` each time. Source/output package roots may already contain `.gitattributes`; use a new results subdirectory. Never execute frozen writer scripts or register these outputs. This runner only reads the KPI/calendar/target spine, original baseline registry files and the side-effect-free K0 engine.

`model.py` profiles one common w in [0,1] while analytically estimating four seasonal coefficients for each candidate. Primary loss is squared USD-million revenue error; the matched fixed model uses exactly the same fitting rule at w=2/3. Relative-error fitting is a separately labeled sensitivity. `run.py` rebuilds all22/exclusion fits, year-block parameter sensitivity, leave-year-out fits, strictly chronological guide-date predictions, matched W1/W2 scores, paired target-year uncertainty and sequential interval coverage. Calendar truncation occurs before building training lags; the target outcome is forbidden. The L2 same-day-letter convention is explicit. K0's existing stricter API uses the documented next-day wrapper and its actual input cutoff is checked.

Core files: `dataset_22.csv`, `parameters.csv`, `profile_loss.csv`, `chronological_paths.csv`, `chronological_scores.csv`, `paired_uncertainty.csv`, `parameter_uncertainty.csv`, `leave_year_out.csv`. Presentation figures are supplied as PNG and SVG. `claim_ledger.csv` includes allowed and forbidden wording; `accepted_validation_spec.json` distinguishes descriptive calibration, validation protocol acceptance, prospective evidence and pending L4/team adoption. `l4_conversion_inputs.csv` contains research-only parameters/evidence with explicit FX/baseline treatment; its joint coefficient specification is not automatically an operational replacement. Null bounds mean unavailable, not zero.

Preregistered methods and pass lines are in `L3_CONVERSION_PREREG_v1.md`; results and independent review notes use new `L3_CONVERSION_*` files. Six calendar-year blocks (one partial), and three/four target-year blocks in W2/W1, yield sensitivity intervals with limited inferential power. w is neither a booking probability nor an actual revenue contribution share; lambda is not commission take rate. Tight full-sample fit is not a forecast edge.

The final canonical research output is `data/processed/forecast_methods/conversion_validation_v1/results_v2`. Full22 USD calibration estimates w=0.78647848 and Q1/Q2/Q3/Q4 conversion rates 12.931911/13.224232/17.302744/12.111558%. The chronological free/fixed RMSE ratios are 1.165407 (W1, n14) and 1.015513 (W2, n10): the preregistered promotion hurdle fails both. Existing fixed operational coefficients remain unchanged. The `final_review_acceptance.json` receipt supersedes only the specification's initial pending independent-review status, binds the accepted files/reviews by SHA-256, and keeps L4/team adoption pending. That review receipt is added after actual independent review, not automatically asserted by a numerical rerun.

## RESUME

Read `L3_CONVERSION_RESULTS_v1.md`, the retained repair note and final independent review/acceptance receipt before consuming the seven L4 rows. Rebuild into a new directory and compare the 24 analytical/presentation files; the independently issued acceptance receipt is evidence for the reviewed version, not a formula output. Preserve the descriptive versus prospective distinction, failed promotion decision, reported-USD embedded FX and existing fixed operational benchmark.
