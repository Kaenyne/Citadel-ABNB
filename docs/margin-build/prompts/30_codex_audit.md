# Codex (gpt-6-astra) audit of the ABNB margin model

Orchestrator command (run from the main tree's shell, stdin closed, generous timeout, background):

```
cd "C:/Users/krish/citadel-abnb-margins" && codex exec --ephemeral -s read-only -C "C:/Users/krish/citadel-abnb-margins" -o docs/margin-build/audit/CODEX_ASTRA_AUDIT.md "$(cat docs/margin-build/prompts/30_codex_audit.md)" < /dev/null
```

---

You are auditing a quantitative model built overnight by other agents. Repository root is your working directory; you have read-only
access; you may run Python (`python` is the repo venv with pandas, statsmodels, scikit-learn; `py -3.13` also exists) to re-compute anything,
but you cannot write files except your final answer, which the harness saves for you. Do not attempt network access. Do not open anything under
`data/raw/theo_onedrive` or `data/raw/licensed` (licensed data).

## Context

Read, in this order: `CLAUDE.md`; `docs/margin-build/00_BRIEF.md`; `docs/margin-build/SYNTHESIS.md`; `docs/margin-build/notes/20_scoreboard.md`;
`docs/margin-build/notes/21_red_team.md`; `docs/margin-build/DISCUSSION.md`; then the method notes under `docs/margin-build/notes/` and the code
under `analysis/src/margin_build/` (start with `23_final_model/` and `10_harness_margin/`). The frozen revenue harness whose calendar and validator
are reused is `analysis/src/forecast_methods/harness/` (its README is authoritative on the registry format). The kill list of numbers that may
never be quoted is `docs/revenue-forecast-strategy/AGENT_BRIEF.md` section 6.

## What to audit (be concrete, reproduce before you assert)

1. Point-in-time integrity of the backtests: any use of a quarter's actuals before its print date, any parameter estimated on the full sample and
   used in a replay labelled PIT, any consensus value dated after the vintage date, any seasonal share or weight computed with future quarters.
2. Arithmetic: adjusted EBITDA equals revenue minus the cash lines minus other add-backs in every forecast row; annuals equal sums of quarters;
   margins equal EBITDA over revenue; EPS bridge consistent (tax, shares); FCF bridge signs; the workbook `model/ABNB_margin_model.xlsx` matches the CSVs.
3. Statistical claims vs n: every "beats baseline" claim has n stated and holds in both windows W1 (n 14) and W2 (n 10) and under both equal and
   recency weighting as the notes claim; quantile coverage claims; whether the combination's leave-future-out weights are actually leave-future-out.
4. Economic coherence: cost-line elasticities have sensible signs and magnitudes; the FY26 margin vs the 35.5% floor is either respected or argued;
   the seasonal profile is applied to the right quarters; the revenue path used is the one the brief names (bridge v3 for 3Q26/4Q26, WS06 v2/v2b for FY27);
   consensus is a comparison column, not an input, outside the method explicitly built on it (M5); the 5 Nov card numbers are traceable.
5. Reproducibility: run `python analysis/src/margin_build/23_final_model/run.py` and `python analysis/src/margin_build/10_harness_margin/score.py`
   (read-only sandbox: if a script tries to write, note the attempt and reason from the code and the committed outputs instead); hard-coded paths;
   missing inputs; scripts that would not run on another machine.
6. Presentation: any kill-list number quoted; any number in SYNTHESIS.md that does not trace to a CSV; overclaiming relative to the evidence.

## Output format (this is saved as `docs/margin-build/audit/CODEX_ASTRA_AUDIT.md`)

Markdown. Start with a five-line verdict (is the model fit to quote in a stock pitch, and what must change first). Then a findings table:
`id | severity (critical / major / minor) | file:line or CSV cell | what is wrong | how you verified | proposed fix`, ordered by severity,
at most 30 findings, each verified (state the command or computation). Then a short section on what the model does well and should keep.
Then a list of the three highest-value improvements that would take under an hour each. No praise padding; be specific.
