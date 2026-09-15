# L0_dolthub_v2: DoltHub consensus history as a second vendor in the L0 vintage register (G1b)

Weekly Sunday snapshots of the ABNB revenue consensus (four period slots) from the public Dolt database
`post-no-preference/earnings`, 2021-02-07 to 2026-09-13, appended to
`data/processed/forecast_methods/L0/L0_vintage_register.csv` with `role=pit_history` and vendor
`DoltHub post-no-preference/earnings`. The vendor string must never contain `zacks` (see run.py).
The L0 folder itself is frozen; this package only imports the frozen loader and calls its append().

Note: `docs/revenue-forecast-strategy/05_backtests/G1b_dolthub_consensus_history.md`.

## Rebuild, in order (run from the worktree root)

```bash
# 0. frozen tests before (this venv's python has no pytest; py -3.13 does)
py -3.13 -m pytest analysis/src/forecast_methods/L0/test_l0.py -q

# 1. T0 provenance (8 + 4 keyless API requests, 10 s apart; already run, results in data/.../t0_provenance*.json)
python analysis/src/forecast_methods/L0_dolthub_v2/t0_provenance.py
python analysis/src/forecast_methods/L0_dolthub_v2/t0_provenance.py --by-message

# 2. dated byte copy of the register (done 14 Sep 2026: L0_vintage_register.backup_2026-09-14.csv)

# 3. build the panel and diagnostics (dry run), then append through the frozen loader
python analysis/src/forecast_methods/L0_dolthub_v2/run.py
python analysis/src/forecast_methods/L0_dolthub_v2/run.py --append        # idempotent: existing ids are skipped

# 4. hard-rule checks + vendor=None behaviour change; frozen tests after
python analysis/src/forecast_methods/L0_dolthub_v2/post_append_checks.py
py -3.13 -m pytest analysis/src/forecast_methods/L0/test_l0.py -q

# 5. T1 vendor equivalence (reads the backup register, the harness calendar and the panel)
python analysis/src/forecast_methods/L0_dolthub_v2/t1_vendor_equivalence.py

# 6. registry baseline l0-dolthub-v2__street_dolthub.csv, then the scorer (py -3.13 has scipy for pit_ks_p)
python analysis/src/forecast_methods/L0_dolthub_v2/register_street_dolthub.py
py -3.13 analysis/src/forecast_methods/harness/score.py

# 7. NCLH sales_estimate pull for WP-E1 (60 s between pages; not appended to the register)
python analysis/src/forecast_methods/L0_dolthub_v2/nclh_pull.py
```

Every script exits 0 on success. `run.py --only-latest` is the T0 FAIL branch (append the latest snapshot
only); it was not needed because T0 passed on attempt 2.

## Outputs (`data/processed/forecast_methods/L0_dolthub_v2/`)

| file | what |
|---|---|
| `dolthub_weekly_panel.csv` | date, slot, period, value_musd, n, high_musd, low_musd, year_ago_musd (1,159 rows) |
| `build_diagnostics.json` | counts, the dropped row, non-Sunday snapshots, T0 status, rows before/after |
| `t0_provenance.json`, `t0_provenance_attempt2.json` | every API query and raw response, the AS OF comparison |
| `post_append_checks.json`, `pit_consensus_vendor_none_delta.csv` | hard-rule invariants; vendor=None lookups before vs after |
| `t1_vendor_equivalence.csv` / `.json` | the 18 pre-guide and 23 at-print cells, register vs DoltHub |
| `scoreboard_before.csv` | the scoreboard as it stood before `register_street_dolthub.py` |
| `dolthub_sales_estimate_NCLH.csv` + `.pull_log.json` | NCLH table for WP-E1 |

## Reading the rows back

```python
import sys; sys.path.insert(0, "analysis/src/forecast_methods/L0"); import l0
l0.pit_consensus("revenue", "2026Q3", "2026-08-06", vendor="DoltHub")   # 2026-08-02 snapshot, 4540.0
l0.pit_consensus("revenue", "2026Q3", "2026-08-06", vendor="Zacks")     # None (frozen test)
l0.pre_guide_street("2026Q3")                                           # LSEG 4610 @ 2026-08-06, unchanged
```

Consumers that call `pit_consensus(..., vendor=None)` now get the DoltHub snapshot wherever it is the latest
vintage strictly before `as_of`; pass `vendor=` or `role=` to reach the register's original press-quote values.
