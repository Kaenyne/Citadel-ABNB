# WS06v: Independent check of the FY27 revenue path v2

Read `docs/margin-build/00_BRIEF.md` first. Slug: `06v_fy27_path_check`. You check WS06's work in
`analysis/src/margin_build/06_fy27_path_v2/`, `data/processed/margin_build/06_fy27_path_v2/`, `docs/margin-build/notes/06_fy27_path_v2.md`.
Do not read WS06's note before you have re-derived the numbers yourself from the same inputs (its prompt lists them: `prompts/06_fy27_path_v2.md`).

## What to do

1. Re-derive independently: 1Q27-4Q27 nights, ADR ex-FX, FX points, GBV, take rate, revenue, base case, from bridge v3 exit + the PR #32 lap
   features + the FX kernel + the ADR v3 card, in your own script `analysis/src/margin_build/06v_fy27_path_check/run.py`. Write your path to
   `data/processed/margin_build/06v_fy27_path_check/06v_independent_path.csv`.
2. Compare with WS06's `06_revenue_path_3q26_4q27.csv` line by line (`06v_diff.csv`: quarter, line, ws06, yours, diff, explanation). Anything
   beyond 0.3pp on a growth rate or $15M on a quarterly revenue level is a finding.
3. Run WS06's `run.py` from clean and check exit code and that its CSVs are reproduced byte-for-byte (or explain the difference).
4. Check point-in-time hygiene: no consensus value used as an input; no kill-list number (`AGENT_BRIEF.md` §6) quoted; sums equal annuals;
   seasonal shares of nights consistent with 2023-25; the 4Q26 rows equal bridge v3 exactly.
5. Check the scenarios: bear/bull symmetric or justified; FX variants correct sign; take-rate asymmetry applied as the pre-registration card states.
6. If you find errors, do NOT edit WS06's files. Write the corrected path as `data/processed/margin_build/06_fy27_path_v2/06_revenue_path_3q26_4q27_v2b.csv`
   (same schema) with a `06_v2b_changes.csv` listing each change, and say in your note which file the margin model should read (`_v2b` if it exists, else the original).
7. Note `docs/margin-build/notes/06v_fy27_path_check.md`: verdict (pass / pass with corrections / fail), numbered findings with severity,
   the diff table, what the margin model must read, "For the model", RESUME.
