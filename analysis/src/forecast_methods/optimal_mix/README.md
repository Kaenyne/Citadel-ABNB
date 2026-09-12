# optimal_mix — leave-future-out forecast combination across the registry

Reads every registered forecast object plus the harness spine and, per target metric,
learns combination weights across methods **and** baselines under leave-future-out
discipline. Writes the winner table, the combined live objects and its own registry
files.

## Run

```bash
cd "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB"
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/optimal_mix/run.py
```

Exit code 0. Idempotent: it overwrites only its own outputs under
`data/processed/forecast_methods/optimal_mix/` and its own `optimal-mix__*.csv`
registry files. It never edits `harness/` or `L0/`, and it drops its own rows from the
registry before reading so it cannot eat its own output.

## Files

| file | contents |
|---|---|
| `combine.py` | the seven weight schemes; pure functions of a training block, no notion of time |
| `run.py` | the replay, the scoring, the winner rule, the live objects, the registration |
| `data/.../optimal_mix/01_candidate_pool.csv` | which candidates entered which pool |
| `…/02_weight_path.csv` | the weight on every candidate at every vintage, every scheme |
| `…/03_scheme_scores.csv` | per (target, pool, window, replay, scheme): n, MAE, RMSE, bias, ratio to naive, CRPS, PIT KS p, 80% coverage, split conformal |
| `…/03b_single_method_scores.csv` | every single candidate on the same quarters |
| `…/04_winner_per_target.csv` | the verdict, with both the oracle and the implementable single-method comparators |
| `…/05_combined_walkforward.csv` | the combined forecast series itself |
| `…/07_replay_pit_vs_fullsample.csv` | the two prior replays side by side |
| `…/combined_live_objects.json` | 3Q26 print, 4Q26 guide midpoint, FY27, multiple implication |

## The rule

A scheme is declared the winner for a target only if it beats the best single candidate
on **both** W1 and W2. Otherwise the file records `BEST SINGLE METHOD IS THE MIX`.
`top1_trailing` is a comparator, not a combination, and may never be declared the winner.

Full results, weights tables and caveats: `docs/revenue-forecast-strategy/05_backtests/OPTIMAL_MIX.md`.
