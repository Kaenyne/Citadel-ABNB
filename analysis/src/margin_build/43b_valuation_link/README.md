# 43b — how the cost leg enters the target price

Run from the repo root:

```
py -3.13 -X utf8 analysis/src/margin_build/43b_valuation_link/run.py
```

Exit code 0; about five seconds. Reads only; writes `data/processed/margin_build/43b_valuation_link/`:

| file | what |
|---|---|
| `43b_target_trace.csv` | each memo price ($143 / $148 / $150 / $138 / $125 / $121 / $137) inverted through the joint solve (A) and expressed as a multiple on the Street's, the official v2's and the 40 short case's FY27 EBITDA |
| `43b_target_checks.csv` | the arithmetic that reproduces the memo's stated numbers |
| `43b_bridge_steps.csv`, `43b_bridge_summary.csv` | spot -> target decomposed into (a) revenue below the Street with costs flexing, (b) costs not flexing, (c) costs above the Street's path, (d) multiple compression; every combination of revenue case x cost path x flex convention x slope (mid, CI low, CI high) |
| `43b_mc_summary.csv` | the corrected Monte Carlo (primary + variants, two seeds) and Jessie's 7 Sep MC replicated and re-scored at today's spot |
| `43b_mc_primary_marginals.csv`, `43b_mc_primary_draws_sample.csv`, `43b_mc_primary_by_bucket.csv` | the primary run's marginals, a 2,000-draw sample, and price by growth x cost-growth bucket |
| `43b_reverse_dcf_implied_margin.csv`, `43b_reverse_dcf_required_growth.csv` | the FY27+ margin today's price implies at Street growth on the repo's `fade_dcf`, and the FY28 growth it needs at each cost-leg margin |
| `43b_scenario_table.csv` | scenario -> FY27 EBITDA -> EV/EBITDA -> $/share, four multiple conventions |
| `43b_meta.json` | spot, shares, net cash, seeds, distributions |

Inputs are hard-coded constants at the top of `run.py`, each with its source file; the two files read at run time are
`data/processed/overnight/13_model_annual.csv` and `13_scenario_grid.csv` (Jessie's MC inputs). Nothing is fitted.
Note: `docs/margin-build/notes/43b_valuation_link.md`.
