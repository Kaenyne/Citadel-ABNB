# B02 — bonus-adr-residual-reverts

- **id:** B02
- **title:** Will 3Q26 reported ADR growth print ≤ +2.0% y/y?
- **type:** binary (bonus item for the short; carries a `## 9. Impact` table); mirror question R07 (≥ +4.4%)
- **resolution date:** 2026-11-05 (3Q26 release, after market close); Yes if 3Q26 ADR ≤ $174.72 on the 3Q25 base $171.29
- **registry entry:** `docs/pitch-forecasts/QUESTIONS.md` § B02
- **batch:** A14 (with B01, B03)

## Files

| path | contents |
|---|---|
| `research-log.md` | revision 1 research log (schema: forecast skill `references/research-log-format.md`) plus §9 Impact |
| `forecasts/2026-09-17-forecast.json` | binary `final`, companion and conditional probabilities, estimates, model, `impact` block, sensitivity, monitoring |
| `datasets/b02_model.py` | the model (numpy/pandas only, seeded); extends R07's `r07_model.py` for the lower tail; `py -3.13 docs/pitch-forecasts/questions/bonus-adr-residual-reverts/datasets/b02_model.py` from the repo root |
| `datasets/b02_results.csv` | history counts, AR(1) fit, card errors split by accel/decel quarter, Gaussian routes, the R07 reproduction, the B02 Monte Carlo, conditionals, sensitivities, the sequential route |
| `datasets/b02_history.csv` | reported ADR y/y, FX, ex-FX, residual, mix terms and the residual needed for ≤ 2.0, 1Q23–2Q26 |
| `datasets/b02_v3_errors_by_direction.csv` | card v3 (with K line) walk-forward errors, midpoint FX, tagged decel/accel |
| `datasets/b02_modest_increase_record.csv` | the five resolved "modest/moderate increase" ADR guides and their prints |
| `sources/` | Polymarket and Kalshi API JSON (2026-09-17T08:03:45Z), `web_queries_2026-09-17.md` (batch web log) |

## Headline (revision 1)

P(3Q26 ADR ≤ +2.0%) = **0.18**, credible interval 0.10–0.30 (model median +3.1%; E[ADR | Yes] +1.3%). Anchor: Bloomberg MODL mean +3.4%, low +1.4% → 0.07. Base rate 0.12 (no quarter since 2023 has printed ≤ 2.0 with FX ≥ −0.5 or a residual ≥ 3.5); structural Monte Carlo 0.18. The number is an FX-estimator question first (euro fit → 0.35; baskets → 0.06) and a residual-reversion question second; the decel-quarter error split does not support a fatter lower tail. Impact if Yes: −2.0pt ADR, 3Q26 GBV −$518M, 4Q26 revenue −$100M, FY27 revenue −$316M, FY26 margin −0.7pp, FY27 −1.3pp, stock ≈ −$12; EV ≈ −$2.2/share — **material**; pair with R07 so the ADR line reads two-sided.
