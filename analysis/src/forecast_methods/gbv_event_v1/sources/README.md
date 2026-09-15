# GE-SOURCE

Canonical note: `docs/revenue-forecast-strategy/05_backtests/GE_SOURCE_RESULTS_v2.md`.

From the worktree root:

```text
python -B analysis/src/forecast_methods/gbv_event_v1/sources/run_v2.py --name inventory_new
python -B analysis/src/forecast_methods/gbv_event_v1/sources/review.py --name review_new
```

Each output name must be new. Writes remain under `data/processed/forecast_methods/gbv_event_v1/sources_v1/`. Inputs are read-only. No model fit, registry or scorer is called. The optional `--probe-yahoo` inventory flag performs one public ABNB query and QQQ only after success; it is unnecessary for reproduction and the retained permitted-network attempt returned HTTP429. No credentials are used.

`run.py` / `run_v1/` preserve the initial inventory attempt. `run_v2.py` / `run_v2/` correct only the event-date inventory field and exclusion of the approximate pre-IPO row. `review.py` independently checks four-quarter arithmetic and daily/source joins without importing the authors' functions; `review_v1/` binds the first reviewed integration and event outputs.
