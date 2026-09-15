# WS21: Red team of every margin method (leakage, PIT, overfitting, kill list)

Read `docs/margin-build/00_BRIEF.md`, `docs/revenue-forecast-strategy/AGENT_BRIEF.md` §6 (kill list), and
`docs/revenue-forecast-strategy/05_backtests/RED_TEAM.md` (the revenue-side red team; same standards). Slug: `21_red_team`. You are adversarial:
your job is to find the reasons each method's accuracy is overstated.

## For every method M1-M7 and the harness (10)

1. **Leakage / PIT.** Read the code. For each input series, does the fit at `vintage_date` use only data knowable then? Check: the WS02 panel
   slice (a quarter's actuals only after its print date); WS03 consensus `street_as_of <= vintage_date`; WS04 alt series `knowable_from`; revenue
   inputs in backtests (must be PIT forecasts, not actuals, unless the spec is labelled revenue-known); seasonal shares computed on the training
   window only; any parameter (elasticity, cushion, k) estimated on the full sample and then applied in a `PIT`-labelled replay. Write a
   reproducible check for each finding (a few lines of Python that demonstrates it) under `analysis/src/margin_build/21_red_team/checks/`.
2. **Overfitting.** Parameters vs n; spec grids where only the best spec was reported; PIT-vs-full_sample gaps; W2-only wins; recency-weighted
   wins that vanish equal-weighted; quantile calibration on n < 10.
3. **Kill list and quoting.** Any kill-list number quoted; any "close to known" quarter; any consensus value used as an input outside M5; any
   licensed raw data copied into `data/processed` or a note (Bloomberg/LSEG raw rows, FactSet text beyond short verbatims).
4. **Reproducibility.** `run.py` exit codes from clean; whether registry files regenerate identically; hard-coded paths; the two-replay rule.
5. **Economic sense.** Signs of elasticities; whether the LIVE margins are consistent with the revenue path the model claims to use; whether
   seasonal profiles are applied to the right quarters; whether the FY26 floor is respected or an argued exception.

## Deliverables

`data/processed/margin_build/21_red_team/21_findings.csv` (id, method, severity critical/major/minor, category, description, evidence path,
proposed fix, affects_ranking yes/no) and note `docs/margin-build/notes/21_red_team.md`: bottom line (which methods stand as-is, which need fixes
before their numbers can be quoted, which are dead), the findings table, the checks you ran (count), a kill-list addendum for this run, RESUME.
Do not fix anything yourself. Address each finding to a method so the discussion round can route it.
