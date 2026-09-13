# A — Guide surprise

From the repository root, using `.venv` Python:

```text
python analysis/src/forecast_methods/alpha_a/run.py
python -m pytest analysis/src/forecast_methods/alpha_a/tests -q
```

This imports the verified `kernel_engine_v2`; it does not re-estimate or copy K0 lambda arithmetic. Historical cutoff is the guide date, strictly before all inputs. An input on that date is refused even if the source says it was available in the morning without an intraday timestamp. Complete per-date abstentions are saved. No `open_*` executable return column exists in the supplied reactions file, so return estimates remain unavailable. The optional next-day arithmetic plot is visibly post-letter and excluded from every pass statistic.

`live_november_guide_scenario.csv` is a September 12 conditional RNPL scenario for the November event, using stamped L0 values. It is not a forecast created on the future event date. Alpha Vantage and Yahoo belong to the same LSEG family and are not independent votes; the designated Alpha Vantage anchor is retained exactly as supplied.

The output-only empty registry template and `registry_status.json` document why no false forecast rows are registered. The frozen harness cannot accept the actual date or the requested gap target. Parent owns scorer, shared board and git. The note states the preregistered line, unavailable statistics and one narrowly scoped proposed memo sentence.
