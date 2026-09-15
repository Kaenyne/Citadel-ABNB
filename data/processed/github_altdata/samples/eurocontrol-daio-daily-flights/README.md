# eurocontrol-daio-daily-flights — sample

Source: https://github.com/euctrl-pru/daio (EUROCONTROL Performance Review Unit). Daily departure / arrival / internal / overflight
flight counts for 40 EUROCONTROL member states, 2019-01-01 to present, auto-committed daily (data through 2026-09-13 at pull).
Pulled 2026-09-14 with curl from raw.githubusercontent.com (files live at the repo root: daio_YYYY.csv and .parquet).
Sample here: daio_2025.csv (14,600 rows) and daio_2026.csv (10,240 rows), plus the upstream README (SOURCE_README.md, column
definitions) and the update script. Total ~1.4 MB, well inside the 25 MB cap; no rows truncated.
Full dataset: the six other yearly CSVs (2019-2024, ~0.8 MB each) via the same raw URL pattern, or
`git clone --depth 1 --filter=blob:none https://github.com/euctrl-pru/daio`.
Licence: none stated in the repo (GitHub license=null); EUROCONTROL data reuse terms need a human check before redistribution.
