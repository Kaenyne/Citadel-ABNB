# 21_red_team — adversarial audit of every margin method and the harness

Interpreter: `py -3.13`. Note: `docs/margin-build/notes/21_red_team.md`.
Outputs: `data/processed/margin_build/21_red_team/` only. **This package fixes nothing** — it reads the
registry, the scoreboard and the method code and writes findings.

## Run

```
cd "C:\Users\krish\citadel-abnb-margins"
py -3.13 analysis/src/margin_build/21_red_team/run.py            # all nine checks, ~3 min, exit 0
py -3.13 analysis/src/margin_build/21_red_team/checks/check_07_survivor_placebo.py   # any check alone
```

Every check takes an optional first argument: a path to a copy of `data/processed/margin_build`
(check 01 takes the `registry` folder inside it), so the audit can be re-run against the state the
methods were in when they were audited rather than against a later re-score.

## The checks

| script | what it establishes |
|---|---|
| `check_01_registry_pit_rules.py` | mechanical PIT rules over all 29 registry files: `knowable_from`/`street_as_of` vs vintage, already-printed quarters, horizon and window consistency, quantile monotonicity, duplicate keys, replays present |
| `check_02_skill_significance.py` | for every margin cell carrying both survive flags: paired loss differential vs seasonal naive, Newey-West(1) t, sign test, block bootstrap |
| `check_03_sentence_rule_information.py` | the quarterly margin sentence quarter by quarter (direction, level, realised y/y) and how often it varies; the quarter-by-quarter decomposition of the guide-policy pin win |
| `check_04_killlist_and_licence.py` | kill-list phrases, "close to known" language, licensed-data markers in tracked paths, `data/raw` exposure |
| `check_05_live_coherence.py` | LIVE margin paths by method vs the FY26 floor, the 3Q26 ceiling sentence, Street, and the historical quarter-of-year ranges |
| `check_06_lines_vs_margin_and_coverage.py` | every line-level MAE ratio beside the same spec's margin ratio; interval calibration against the binomial band attainable at n=14 / n=10 |
| `check_07_survivor_placebo.py` | sign-flip null distribution of the number of `survives_both_windows` cells — how free the flag is |
| `check_08_reproducibility_inputs.py` | which packages' `run.py` depend on gitignored raw inputs with no re-pull fallback |
| `check_09_m1_step_dummy_leak.py` | the vintages at which M1's `d_steps_rw` uses a step dummy that was not yet knowable |

## Outputs

| file | what |
|---|---|
| `21_findings.csv` | id, method, severity, category, description, evidence path, proposed fix, affects_ranking |
| `21_reproducibility.csv` | every package's `run.py` replayed from this worktree: exit code, wall time, whether its outputs regenerated identically |
| `21_check_output.txt` | the full captured output of all nine checks |
| `21_check_index.csv` | one row per check: exit code, seconds, what it establishes |
