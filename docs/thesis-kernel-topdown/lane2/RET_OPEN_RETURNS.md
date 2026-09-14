# RET — Executable next-open returns: verify, optionally refresh (run by the parent; Gate 1, part 2)

**Role in Lane 2:** A2 and B2 report return legs only from this file. Gate 1 confirms it exists, ties out, and (if the sandbox has
internet) is current to yesterday's close.

## Files this agent reads
- `analysis/src/forecast_methods/returns_v1/README.md`, `returns_v1/tests/`
- `data/processed/forecast_methods/returns_v1/{ohlc_daily.csv, earnings_reactions_open_v1.csv, manifest.json}`

## Task
```bash
python -m pytest analysis/src/forecast_methods/returns_v1/tests -q          # expect 8 passed (offline, committed data)
python analysis/src/forecast_methods/returns_v1/run.py                       # exit 0; 23 events
# only if outbound network works AND it is a trading day after the manifest's last_date:
python analysis/src/forecast_methods/returns_v1/run.py --refresh             # re-fetch OHLC; re-run the tests; commit the refreshed files
```
Record in the run log: the manifest's `retrieved_at_utc` and `last_date`, the 23-event count, and the legacy tie-out line the test prints
(median |diff| ≈ 0.03pp against `abnb_earnings_reactions.csv`).

## Pass line (pre-registered)
8 tests green · 23 events · every `entry_date` strictly after its `event_date` · `excess_open_*` = ABNB − QQQ to 1e-9. Anything else → STOP.

## Outputs
A section in `05_backtests/LANE2_RUN_LOG.md`; refreshed data files only if `--refresh` ran.
