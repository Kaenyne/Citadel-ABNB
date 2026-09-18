# R07 — risk-adr-residual-persists

- **id:** R07
- **title:** Will 3Q26 reported ADR growth print ≥ +4.4% y/y (consensus +3.4%; team +3.3%)?
- **type:** binary (risk to the short; carries a `## 9. Impact` table); mirror question B02 (≤ +2.0%)
- **resolution date:** 2026-11-05 (3Q26 release, after market close)
- **registry entry:** `docs/pitch-forecasts/QUESTIONS.md` § R07
- **batch:** A10 (with R04, R05)

## Files

| path | contents |
|---|---|
| `research-log.md` | revision 1 research log (schema: forecast skill `references/research-log-format.md`) plus §9 Impact |
| `forecasts/2026-09-17-forecast.json` | binary `final`, companion and conditional probabilities, estimates, model, `impact` block, sensitivity, monitoring |
| `datasets/r07_model.py` | the model (numpy/pandas only, seeded); `py -3.13 docs/pitch-forecasts/questions/risk-adr-residual-persists/datasets/r07_model.py` from the repo root |
| `datasets/r07_results.csv` | base-rate counts, card walk-forward RMSE/bias by FX estimator, Gaussian routes, structural Monte Carlo and its sensitivities |
| `datasets/r07_history.csv` | reported ADR y/y, FX effect, disclosed ex-FX and the pricing residual 1Q23–2Q26, with the FX-neutral test |
| `datasets/r07_v3_errors.csv` | card v3 (with K line) walk-forward errors on reported dollar y/y, midpoint FX, 1Q24–2Q26 |
| `sources/` | Kalshi and Polymarket API JSON (2026-09-17T03:34:27Z), `web_queries_2026-09-17.md` (shared batch web log) |

## Headline (revision 1)

P(3Q26 ADR ≥ +4.4%) = **0.17**, credible interval 0.10–0.28 (model median +3.1%; P(≤ +2.0%) ≈ 0.17). Anchor: Bloomberg MODL mean +3.4% / high +4.6% → 0.12. Base rate 0.09 (no FX-neutral quarter since 2023 has reached +4.4 ex-FX); structural Monte Carlo 0.14. The number is an FX-estimator question first (baskets +0.26 → 0.27; euro fit −1.12 → 0.02) and a residual question second. Impact if Yes: +1.1pt ADR, 4Q26 revenue +$50M, FY27 revenue +$174M, FY27 margin +0.7pp, stock ≈ +$7; EV ≈ +$1.2/share — **marginally material**.
