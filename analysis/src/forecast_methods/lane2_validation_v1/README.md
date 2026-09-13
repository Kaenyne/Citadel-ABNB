# Lane 2 portable verification

Run from the repository root using the repo venv:

```sh
python -X utf8 analysis/src/forecast_methods/lane2_validation_v1/run.py --stage gate1 --tests
python -X utf8 -m pytest analysis/src/forecast_methods/lane2_validation_v1/tests -q
python -X utf8 analysis/src/forecast_methods/lane2_validation_v1/run.py --stage close
```

The wrapper calls the actual existing frozen and FORMAT 1.1 scorer `main()` functions in that order. Only their output destinations are redirected into the new validation snapshot directory; inputs, registry loading, arithmetic and frozen source files are unchanged. The same applies to the existing RET rebuild. No registration is performed.

Every original scoreboard row must remain present. Text, booleans, integers, keys and missingness match exactly; floating metrics differ by strictly less than 1e-9 absolute, with zero relative tolerance, following the committed FORMAT 1.1 equivalence test. Frozen file hashes must match before/after, including on failures. New method rows are allowed after packages register, but old rows cannot disappear. Original failure receipts remain in LANE2_RUN_LOG.md; the correction and preregistration are in LANE2_RUN_LOG_v2.md.

Outputs: per-stage scorer CSVs/Markdown/stdout, test receipts, rebuilt returns, frozen-file SHA-256 manifests and summary.json. A failed run preserves an explicit FAIL summary. Use a new stage name to preserve an earlier stage's outputs.
