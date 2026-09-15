# L3 integration and audit

All work is on `codex/lane3-full`, based on verified published L1/L2 commit `1c87628cedbc94ab8a0e8552743c94485ef353b8`. No ABNB forecasts are registered here.

Use Python with pandas, numpy, scipy, statsmodels and pytest. Package runners accept new output directories and preserve existing research. The parent interpreter in this Windows workspace is `C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe`.

```powershell
python -m pytest analysis/src/forecast_methods/l3_integration_v1/test_bundle.py -q
python analysis/src/forecast_methods/l3_integration_v1/score_snapshot.py --out outputs/l3_scores_NEW
python analysis/src/forecast_methods/l3_integration_v1/provenance.py --compare data/processed/forecast_methods/l3_integration_v1/start_hashes.json --external-fx 'C:/Users/wille/Desktop/Citadel - ABNB/FX_ENGINE_SESSION_BUNDLE' --out outputs/l3_hashes_NEW.json
```

The score wrapper executes the actual frozen scorer followed by FORMAT1.1 with only output destinations redirected. It compares all 284 rows against the committed L2 close board: exact keys/counts/flags/missingness, floats <1e-9 absolute with rtol0. `--tests` additionally runs the existing 155 frozen/L0/FORMAT/kernel/returns tests. None of their sources or score files is changed. Those tests and scores already passed in `data/processed/forecast_methods/l3_integration_v1/score_check/`.

The provenance command hashes every base-commit file and the optional explicit external FX bundle. These are source-worktree byte hashes, hence line-ending-specific. To compare the saved receipt in this same source worktree, supply the same external bundle path. External R examples are not runtime inputs to the new cohort engine and are not included in the Git change.

`run.py --out outputs/l3_reproduction_NEW` runs all five package tests and offline runners into new directories, preserving command/exit/time/stdout receipts. Optional `--fx-bundle PATH` adds the read-only R interface manifest; it does not change any scenario economics.

`bundle.py` takes five `--input PACKAGE=PATH` arguments (`cohort_fx`, `fee_panel`, `adr_hotel`, `nclh`, `conversion`) and `--out NEW_DIRECTORY`. It requires committed clean research inputs/sources, normalizes metadata names, validates semantic keys/date/units/bounds/treatment, copies canonical package outputs into its payload, and saves SHA256SUMS. A bundle-local `.gitattributes` preserves exact bytes across Git checkouts. Validate with `python .../bundle.py --verify --out BUNDLE_DIRECTORY`. Payload checksum excludes only the root checksum manifest itself. Original source periods/timestamps and other columns are preserved; L3 analysis information_date is September13.

L4 owns every model choice, combined forecast, guide, memo and registry entry. The highest-priority conversion payload separates the audited 22-quarter descriptive calibration from chronological promotion and the retained fixed 2/3-1/3 operational benchmark. It includes parameter/year sensitivity, predictive-interval diagnostics, presentation charts, and an allowed/forbidden claim ledger. The bundle also contains conditional FX and ADR alternatives, unavailable fee theta, and cross-issuer/comparator evidence. A schema or implementation PASS never adopts those assumptions.
