# 22_discussion_group_A — reproduction scripts for the WS22 group A discussion

Two small scripts behind the numbers in `docs/margin-build/discussion/group_A.md` and in the
"Discussion response" sections of `docs/margin-build/notes/{M1_driver_lines,M4_alt_augmented,M6_cycle_flex}.md`.
They read only the harness scoreboard and the registry; they write nothing else and register nothing.

```bash
cd "C:\Users\krish\citadel-abnb-margins"
py -3.13 analysis/src/margin_build/22_discussion_group_A/repro_skill.py   # -> groupA_paired_tests.csv
py -3.13 analysis/src/margin_build/22_discussion_group_A/repro_drift.py   # -> groupA_paired_vs_drift.csv
```

Interpreter `py -3.13` (needs `scipy.stats`). Outputs land in
`data/processed/margin_build/22_discussion_group_A/`.

| script | what it establishes |
|---|---|
| `repro_skill.py` | R01/R02 on group A's own cells. Paired loss differentials `d_q = abs(e_method) - abs(e_seasonal_naive)` on `adj_ebitda_margin_pct`, h=0, PIT, per (method, object, spec, window), with a Newey-West(1) t, its p, and a two-sided sign test. Largest W1 abs(t) among M1/M4/M6 is 0.86 and every W1 p exceeds 0.38. |
| `repro_drift.py` | R14 re-scored against `seasonal_naive_drift` (the honest baseline for a growing dollar line) rather than `seasonal_naive`, for the five cash lines, total cash costs, adj EBITDA $ and the margin, h=0, PIT. Only **cost of revenue** survives: M6 `l0_rw` ratio 0.652 (W1) / 0.677 (W2), t -3.57 / -2.67, better in 13/14 and 9/10. Product development, S&M and total cash costs are **worse** than the drift naive in every method. |

Both read `data/processed/margin_build/10_harness_margin/scoreboard_by_quarter.csv` and, for the drift baseline,
`data/processed/margin_build/registry/baselines-margin__seasonal_naive_drift.csv`, so they must be re-run after
`score.py` if the numbers are to be re-quoted. The cells they report on (`b_elastic_rw`, `l0_rw`, `none_rw`,
`best1_rw`, `ridge_all_eq`) were **not** changed by the WS22 fixes, so the re-score should reproduce these
numbers exactly; the oracle rows (`e_revknown_rw`, `revknown_rw`) will simply disappear from the output, since
they are no longer registered.
