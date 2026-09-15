# L4 local integration control v2

This parent-owned package preserves all completed L4/L1/L2 files while the new version consumes accepted L3 Git objects. It changes no research parameter and authors no workbook. Run from the L4 worktree root with the repository Python environment. Every snapshot name must be new.

```powershell
python -B -X utf8 analysis/src/forecast_methods/lane4_control_v2/run.py init --snapshot baseline
python -B -X utf8 analysis/src/forecast_methods/lane4_control_v2/run.py verify --snapshot close
```

`init` belongs only at the exact supplied starting commit; it records every pre-existing tracked file and registry CSV. Later verification checks those bytes, the original external read-only FX dependency, and the explicit L3 Git manifest/ancestry. Do not repeat an existing snapshot or recapture the baseline after work is complete.

If genuinely new forecast objects are registered, add `--score` to the final verification: it runs both actual unchanged scorers to new output folders and checks every old historical score with exact keys/missingness and absolute tolerance below 1e-9, zero relative tolerance. Without registry changes, preserved historical files/registrations make broad scorer/test repetition unnecessary. Source, financial and artifact-specific checks are reported separately.

## Independent integration and export checks

`review_revenue.py` verifies the frozen output/source hashes, preserved baseline,
same-object expectations arithmetic, named fixed-K0 scenario attribution, isolated
net sensitivities and all 1,000 intact accepted parameter tuples across three
quarters. This audits propagation only; it does not fit conversion or repeat L3
historical tests.

`review_exports.py` reads the exported XLSX's OOXML formula caches using the
previously reviewed read-only parser. It independently selects the dated LSEG
panel, derives September cash/shares and value from annual CSVs, checks nine case
captures and the visible live formulas, rejects error cells/external links, and
checks stale-capture status. It does not claim a native Excel session was run.

`review_staging.py` compares each staged blob with the reviewed working file
and refuses modifications to pre-existing files, oversized/prohibited inputs,
or unexpected Git diagnostics. Its explicit preservation policy records Git's
raw whitespace exit and permits CRLF-only serialization plus cosmetic whitespace
in frozen/copied text artifacts. It never normalizes accepted source bytes.
The first strict whitespace failure remains in `staging_review_v1.json`.

Use the final workbook snapshot specified in `L4_CLOSE_HANDOFF_v2.md`; every
receipt path must be new. Example from the worktree root:

```powershell
python -B -X utf8 analysis/src/forecast_methods/lane4_control_v2/review_revenue.py --revenue-dir data/processed/forecast_methods/lane4_revenue_v2/snapshot_v1 --output data/processed/forecast_methods/lane4_control_v2/revenue_review_new.json
python -B -X utf8 analysis/src/forecast_methods/lane4_control_v2/review_exports.py --workbook model/lane4_v2/outputs/lane4_model/snapshot_v2/ABNB_L4_review.xlsx --model-dir data/processed/forecast_methods/lane4_model_v2/snapshot_v2 --revenue-dir data/processed/forecast_methods/lane4_revenue_v2/snapshot_v1 --output data/processed/forecast_methods/lane4_control_v2/export_review_new.json
```

## RESUME

Use the explicit source and final artifact versions in the new L4 handoff. Preserve the benchmark, source hashes and previous artifacts. Public publication remains unauthorized; this work ends with a local reviewed commit. Do not retry public push or create a PR until the user separately authorizes that destination.
