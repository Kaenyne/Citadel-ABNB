# Lane 1 parent scoring adapter

From the repo root using `.venv` Python:

```text
python analysis/src/forecast_methods/lane1_control_v2/run.py --stage after-a
```

The original scorer writes existing frozen output files. This adapter copies its
source and required tracked inputs into a temporary repo layout, verifies every
copy with SHA-256, runs the original `harness/score.py` unchanged, checks that real
inputs have not changed, and saves the score and receipt to a new stage folder.
It includes newly registered CSVs and refuses to overwrite a prior checkpoint.
No new forecast method or scoring formula is introduced. This preserves the
copy-only constraint while actually executing the requested frozen scorer.
