# B08 — bonus-ai-hosting-cost-step

- **id:** B08
- **title:** By the Feb print, will management quantify incremental AI/hosting/infrastructure spend for FY27 of ≥$50M, or will 4Q26 cost of revenue grow ≥ +18% y/y (≥ $575M on 4Q25's $487M)?
- **type:** binary (bonus for the short; carries a `## 9. Impact` table)
- **resolution date:** ~2027-02-11 (4Q26 release and call)
- **registry entry:** `docs/pitch-forecasts/QUESTIONS.md` § B08
- **batch:** A16 (with B09, B10, B17)

## Files

| path | contents |
|---|---|
| `research-log.md` | revision 1 research log (schema: forecast skill `references/research-log-format.md`) plus §9 Impact |
| `forecasts/2026-09-17-forecast.json` | binary `final`, companion leg probabilities, estimates, model, `impact` block, sensitivity, monitoring |
| `datasets/b08_model.py` | the model (numpy/pandas only, seeded); `py -3.13 docs/pitch-forecasts/questions/bonus-ai-hosting-cost-step/datasets/b08_model.py` from the repo root |
| `datasets/b08_results.csv` | leg-2 Monte Carlo and sensitivities, ratio base rates, leg-1 conditionals |
| `datasets/b08_history.csv` | cost of revenue, GBV and the cost-of-revenue/GBV ratio by quarter 1Q23–2Q26 with y/y changes |
| `sources/` | Kalshi and Polymarket API JSON (2026-09-17T08:21:21Z), `web_queries_2026-09-17.md` (shared batch web log) |

## Headline (revision 1)

P(Yes) = **0.38**, credible interval 0.25–0.52. Leg 2 (4Q26 cost of revenue ≥ $575M) ≈ 0.26 (median $559M); leg 1 (a quantified ≥ $50M FY27 AI/hosting step) ≈ 0.24. Anchor: the line build's reconciled 4Q26 path ($578M, +18.7%) → 0.63; the log discounts the reconciliation step because the contracted hosting step is a 2027 event. Impact if Yes: FY27 margin −0.6pp, EPS −$0.14, stock ≈ −$4; EV ≈ −$1.5/share — **material at the margin**, keyed to the 5 Nov cost-of-revenue print.
