# govdata_v2: EUROCONTROL daio daily flights as an EMEA nights feature (build C)

Copy of the govdata V protocol (`analysis/src/govdata/V1_collect.py`, `V2_backtests.py`, `V3_rank.py`, frozen there) narrowed to one new source: `https://github.com/euctrl-pru/daio`, daily flight counts per EUROCONTROL state, 2019-01-01 to yesterday. Pre-registration and results: `docs/revenue-forecast-strategy/05_backtests/C2_eurocontrol-daio.md`.

## Run

```
cd "C:/Users/krish/citadel-abnb-ghcat"
git clone https://github.com/euctrl-pru/daio "C:/Users/krish/abnb_ia_capture/euctrl_daio_git"   # once; full history, about 130 MB
python analysis/src/govdata_v2/run.py
```

Exit code 0 on success; about two minutes, most of it C2 reading yearly files out of git history.

| Step | What | Writes (all under `data/processed/govdata_v2/`) |
|---|---|---|
| `C1_collect.py` | pulls `daio_2019.csv` to `daio_2026.csv` from raw.githubusercontent.com into `data/raw/eurocontrol_daio/` (gitignored; skipped when present), manifest with sha256, daily `eu40` and `eu_core` sums of `flt_da`, 2025 country weights | `raw_manifest.csv`, `daio_daily_aggregates.csv`, `country_weights_2025.csv` |
| `C2_vintages.py` | git-history revision check (last 7 days of a yearly file between commits about a week apart) and the point-in-time qtd75 reading per quarter from the first commit whose data reaches day 75 | `git_commits.csv`, `revision_check.csv`, `revision_summary.csv`, `qtd75_pit.csv` |
| `C3_backtests.py` | quarterly feature panel, T0 duplicate check against the held Eurostat `avia_paoc`, walk-forward backtests on both govdata windows against `emea_nights_yoy_mid` and `total_nights_yoy` via `analysis/src/adrq3/I0_protocol.py`, 3Q26 readings | `C_feature_panel.csv`, `C_t0_duplicate_check.csv`, `C_backtests.csv`, `C_readings_3q26.csv` |
| `C4_rank.py` | pre-registered pass line applied, live reading table | `C_candidates.csv`, `C_ranked_table.md`, `C_live_reading.csv` |

`eu_core` = EU27 + UK + CH + NO (29 rows in the file, Belgium and Luxembourg being one). Excluded from it: Israel, Morocco, Ukraine, Moldova, Georgia, Armenia, Turkiye, Albania, Serbia and Montenegro, Bosnia-Herzegovina, North Macedonia. The measure is `flt_da` (departures plus arrivals); overflights and internal flights are excluded.

Licence: the upstream repo carries no LICENSE and the counts derive from EUROCONTROL network data; raw files stay under `data/raw/` (gitignored). Only the derived aggregates, the manifest and the weights table are committed (WP-O log line pending).
