# X01 — scenario-probabilities

- **id:** X01
- **title:** What are the probabilities of the memo's three scenarios for the 5 Nov print: thesis breaker, base, short case (plus none of the above)?
- **type:** multiple choice over {thesis breaker, base, short case, none of the above}; synthesis question, runs last and reads every other forecast
- **resolution date:** 2026-11-05 (the 3Q26 letter: printed nights, 4Q26 nights descriptor, 4Q26 revenue midpoint vs the 4 Nov Street mean, FY26 margin sentence)
- **registry entry:** `docs/pitch-forecasts/QUESTIONS.md` § X01
- **batch:** A19

## Files

| path | contents |
|---|---|
| `research-log.md` | revision 1 research log (schema: forecast skill `references/research-log-format.md`); §0b fixes the seven conventions that make the four options mechanically resolvable, §6 has the joint structure, the marginal checks, the option × print / C01 / C02 / C04 tables and the scenario table for the memo |
| `forecasts/2026-09-17-forecast.json` | revision 1: MC `vector`, the alternative "material" reading, `scenario_table` (per option: P, day-1 median, P(≤ −8%), P(≥ +5%), 15 Dec conditional median, and the probability-weighted 15 Dec close), marginal checks, joint structure, estimates, sensitivity, monitoring |
| `datasets/x01_joint.py` | the joint simulation (numpy + stdlib, seed 20260917, n 1,000,000): print N(9.5, 1.70) → C01 (gap model, slope from C01's own structure, intercept solved to 0.72) → C02 (log-odds in nights through C02's branch table, IPF to its final vector, OR 2 on C01) → C04 (published conditionals on C01) → classification with precedence → S01 cell day-1 return → S02 branch 15 Dec close; plus the reaction-panel base-rate construction and 27 single-assumption re-runs. `py -3.13 docs/pitch-forecasts/questions/scenario-probabilities/datasets/x01_joint.py` from the repo root (~4 min) |
| `datasets/x01_joint_summary.json` | every number the log quotes: vector, scenario table, marginal checks, compositions, joint tables, base rates, sensitivities, inputs |
| `datasets/x01_joint_table.csv` | option × (print state, C01, C02, C04) joint masses |
| `datasets/x01_scenario_table.csv` | per-option conditional day-1 and 15 Dec statistics |
| `datasets/x01_sensitivity.csv` | the 27 re-runs (print centre/sd, C01 level and slope, C02 dependence and (a)/(d) mass, C04 (d) mass and print link, precedence, material reading, gate placements, seed) |
| `datasets/x01_base_rate_panel.csv` | the 16 ex-reopening prints 3Q22–2Q26 classified into the four cells under the literal and the material readings |

## Headline (revision 1)

**thesis breaker 0.14 / base 0.22 / short case 0.55 / none of the above 0.09** (literal reading: short case = printed nights ≤8.5% OR C02 (d) OR C04 (d); precedence breaker > short > base > none). Material reading (C02 leg = explicit mid-single bucket only): 0.14 / 0.26 / 0.49 / 0.11. Memo anchor 25 / 45 / 30 / 0.

The joint reproduces every input: print states 0.615 / 0.125 / 0.261, C01 0.721, C02 0.180 / 0.170 / 0.300 / 0.310 / 0.040, C04 0.335 / 0.297 / 0.047 / 0.271 / 0.050, C04 (d) | below 0.317, S01 breaker cell 0.113. Reaction-panel base rate (W2, n 10) 0.10 / 0.20 / 0.50 / 0.20.

Scenario table: breaker day-1 median +2.2% (P(≤ −8) 0.12, P(≥ +5) 0.37), 15 Dec $175; base −3.8% (0.32 / 0.17), $162; short case −3.8% (0.33 / 0.18), $162; none +1.2% (0.15 / 0.33), $173; probability-weighted 15 Dec $164.8. Base and short case are identical on the day because S01 prices the print state and the guide sign, not the descriptor wording or the margin sentence.
