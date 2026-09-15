# 03_consensus_pit — point-in-time Street consensus for ABNB margins (WS03, margin build 13 Sep 2026)

Rebuild everything (from the worktree root):

```bash
python analysis/src/margin_build/03_consensus_pit/run.py
```

`run.py` skips the LSEG pull when the 35 raw files already sit in `data/raw/margin_build/03_consensus_pit/`
(licensed, gitignored; manifest with sha256 in `data/manifests/margin_build/03_consensus_pit.csv`).
To re-pull, delete the raw folder and run again with the LSEG Workspace desktop open and `LSEG_APP_KEY` set;
the pull itself runs under `py -3.13` (`lseg-data 2.1.1`) and never prints the key.

| file | what |
|---|---|
| `pull_lseg.py` | raw pull: ABNB daily 2021-01-04..2026-09-13, periods FQ1-FQ4 and FY1-FY3 (each row carries `.calcdate`, `.fperiod`, `.periodenddate` and per-field `.date`); actuals via FQ0/FY0; BKNG/EXPE monthly FQ1/FY1/FY2 |
| `build.py` | derives every table in `data/processed/margin_build/03_consensus_pit/` (see the note for the schema) |
| `figures.py` | three PNGs in `analysis/figures/margin_build/03_consensus_pit_*.png` (py -3.13, matplotlib) |

Outputs (all derived; no raw licensed rows):
`03_consensus_at_dates.csv`, `03_L0_append_candidates.csv`, `03_surprise_history.csv`, `03_revision_paths.csv`,
`03_surprise_stats.csv` / `.json`, `03_flowthrough_regressions.csv`, `03_fy_floor_anchoring.csv`,
`03_current_consensus.csv`, `03_bloomberg_anchoring_test.csv` (+ `_rows`), `03_peer_consensus_monthly.csv`, `03_pass_line.json`.

Note: `docs/margin-build/notes/03_consensus_pit.md`.
