# GE conditional LIVE registration and unchanged-scorer audit

Canonical model: `data/processed/forecast_methods/gbv_event_v1/integration_v2/model.json`. Canonical audit: `data/processed/forecast_methods/gbv_event_v1/scoring_v1/`. Seven point-only LIVE PIT rows under new method `gbv-event-v1`: four `revenue_musd` forecasts and three future `guide_mid` forecasts. No already-issued Q3 guide is registered. Vintage15September2026; input cutoff13September. No calibrated probabilities or promotion.

Initial registration was executed once:

```powershell
python -B -X utf8 analysis/src/forecast_methods/gbv_event_v1/registry_scoring/run.py --mode register --out data/processed/forecast_methods/gbv_event_v1/scoring_v1
```

The registered objects now exist. To reproduce checks without overwriting/re-registering them:

```powershell
python -B -X utf8 analysis/src/forecast_methods/gbv_event_v1/registry_scoring/run.py --mode audit-existing --out data/processed/forecast_methods/gbv_event_v1/scoring_reproduction_NEW
python -B -X utf8 analysis/src/forecast_methods/gbv_event_v1/registry_scoring/test_registry_scoring.py
```

The model path is configurable with `--model`; its four-quarter identity, vintage and accounting formulas are enforced. `--mode register` refuses any pre-existing object and uses exclusive creation. `audit-existing` first verifies exact registered bytes against the authoritative FORMAT1.1 writer's reconstructed output. It never modifies them. Every audit output ID must be new.

Both unchanged scorer `main()` functions run before/after. Only their runtime OUT_CONFORMAL_GRID/OUT_SCOREBOARD/OUT_SCOREBOARD_MD destinations are redirected into new audit folders; no frozen source or checked-in scoreboard is modified. Standard FORMAT1.1 validation/writing prepares the CSVs. Registration is point-only with q50 equal to point solely to satisfy the format; no other quantile/SD field is populated. Horizons are calendar-quarter offsets0/1/2/3 from2026Q3. n_params=5 describes the entire four-season-lambda/shared-cushion path. n_train holds each seasonal lambda's5/6 observations; cushion training8 is separately stated in notes, not added into a fabricated independent sample count.

`preexisting_scoreboard_drift.csv` compares checked-in scoreboards to the baseline computed before this registration. Its differences are separate from before/after registration and cross-format checks. See `GE_REGISTRY_SCORING_v1.md` for exact results. Python requires pandas/NumPy/SciPy and the existing harness dependencies; SciPy must be present so PIT p-values do not silently become unavailable.
