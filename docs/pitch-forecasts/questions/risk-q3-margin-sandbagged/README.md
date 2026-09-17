# R05 — risk-q3-margin-sandbagged

- **id:** R05
- **title:** Will 3Q26 adjusted EBITDA margin print ≥ 51.5% (i.e., "down slightly" was sandbagged by ≥1.4pp vs 3Q25's 50.09%)?
- **type:** binary (risk to the short; carries a `## 9. Impact` table)
- **resolution date:** 2026-11-05 (3Q26 release, after market close)
- **registry entry:** `docs/pitch-forecasts/QUESTIONS.md` § R05
- **batch:** A10 (with R04, R07)

## Files

| path | contents |
|---|---|
| `research-log.md` | revision 1 research log (schema: forecast skill `references/research-log-format.md`) plus §9 Impact |
| `forecasts/2026-09-17-forecast.json` | binary `final`, companion probabilities, estimates, model, `impact` block, sensitivity, monitoring |
| `datasets/r05_model.py` | the model (numpy/pandas only, seeded); `py -3.13 docs/pitch-forecasts/questions/risk-q3-margin-sandbagged/datasets/r05_model.py` from the repo root |
| `datasets/r05_results.csv` | base rate, Gaussian routes on the card / M5 / Street, cost-stack Monte Carlo and its sensitivities, the revenue-leg cost arithmetic |
| `datasets/r05_ceiling_record.csv` | the ten quarterly ceiling sentences 3Q22–4Q25 with realised y/y margin change and excess over the ceiling |
| `sources/` | Kalshi and Polymarket API JSON (2026-09-17T03:34:27Z), `web_queries_2026-09-17.md` (shared batch web log) |

## Headline (revision 1)

P(3Q26 margin ≥ 51.5%) = **0.17**, credible interval 0.10–0.27. Anchor: M5 Street-plus-bias composite 50.19% → 0.16. Base rate 0.17 (ceiling sentences exceeded by ≥1.4pp: 0–1 of 10); cost-stack Monte Carlo 0.19. A 51.5% print at the team's $4,804M needs cash costs ≤ $2,330M (−$75M vs budget), i.e. S&M ≤ $706M (+20.7% y/y vs +33.5% budgeted). Impact if Yes: FY26 margin +0.5pp, FY27 +0.4pp, stock ≈ +$3; EV ≈ +$0.5/share — **immaterial**.
