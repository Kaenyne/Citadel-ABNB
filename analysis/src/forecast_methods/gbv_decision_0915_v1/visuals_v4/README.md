# Accepted GBV decision figures

Run `run.py --out <new-directory>` from the worktree root using the main repo's `.venv/Scripts/python.exe`. The accepted command used `--out outputs/gbv-decision-20260915-v4`. That destination exists and must not be overwritten.

Produces five PNGs plus `GBV_decision_visuals.pdf`, with a source/output hash manifest. Sources are the reviewed immutable horizon, Street and flight tables. All error charts explicitly describe raw midpoint RMSE; a separate rounding sensitivity leaves conclusions unchanged. Numeric point spread, known-input exposure and unavailable perfect-GBV diagnostics are not predictive intervals or observed cohort shares.

This final version uses literal dollar text, correct legend placement, a shorter figure05 title and an appropriately conditional statement about better future GBV. All five figures were visually checked through the rendering iterations, and the final affected figure was re-inspected. Previous code/render versions are preserved. Current fitted weights in figure01 are supported by `horizon_v1/results_v2/origin_fits.csv` (15September row).
