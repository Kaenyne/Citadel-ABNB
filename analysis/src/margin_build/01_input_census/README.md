# 01_input_census

Census of every repo input that could bear on an Airbnb cost line, an add-back or a below-EBITDA item
(margin build run, 13-14 Sep 2026, WS01).

Rebuild (from the worktree root; `python` = repo venv 3.11 with pandas):

```
python analysis/src/margin_build/01_input_census/run.py
```

Exit code 0 means: every `file_path` and `script_path` in the census exists, both CSVs have the required columns,
and at least 10 gap rows carry a concrete source string. The registry is inline in `run.py`; first/last period and n
are read from each file at run time (period column auto-detected or given by `pcol`).

Outputs (`data/processed/margin_build/01_input_census/`):

- `01_input_census.csv` — one row per series/file (123 rows): series_id, description, file_path, script_path, frequency,
  first_period, last_period, n_obs, pit_lag_days, target_lines, mechanism, prior_evidence, status, suggested_method.
- `01_gaps.csv` — inputs not in the repo (26 rows) with a concrete source (URL pattern / LSEG field / EDGAR form), reachability
  under the brief's rules, and the WS04 action.
- `01_census_summary_by_line.csv` — counts of series and gaps per target line.

Target-line codes: `cor` cost of revenue, `ops` operations & support, `pd` product development, `sm_brand` brand + performance
marketing, `sm_field` field operations & policy, `ga` G&A, `sbc`, `da`, `addbacks`, `int_inc` interest income, `other_inc`,
`tax`, `shares`, `fcf_timing` (unearned fees / funds payable / working capital), `capex`, `rev_drivers` (nights, GBV, ADR,
take rate, FX, mix), `margin_total`, `guide` (guidance / consensus / language).

Note: `docs/margin-build/notes/01_input_census.md`.
