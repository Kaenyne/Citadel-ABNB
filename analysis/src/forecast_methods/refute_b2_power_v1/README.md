# B2 power refuter

From the repository root, using the repository virtual environment:

```text
.venv\Scripts\python.exe analysis/src/forecast_methods/refute_b2_power_v1/run.py
```

Reads B2's metadata-corrected event cells and the source next-open return file. Independently rebuilds ratios, counts, Wilson intervals, exact-binomial planning power and return uncertainty. Source return equality, window nesting and headline arithmetic are asserted. Creates a new timestamped output folder on every run, including SHA-256 input hashes and the full post-hoc diagnostic grid. No statistical functions are imported from B2; no forecasts are registered and neither scorer is run.

Preregisration: `docs/revenue-forecast-strategy/05_backtests/REFUTE_B2_power_PREREG.md`. Final note: `REFUTE_B2_power.md` in that directory. The source package's own specification inventory is distinguished from additional post-hoc refuter diagnostics. Independent Bernoulli/normal power calculations are illustrative planning benchmarks; they do not establish independence for this series.
