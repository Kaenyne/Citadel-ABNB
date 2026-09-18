# R04 — risk-single-fee-take-rate-accretion-stated

- **id:** R04
- **title:** Will management state at the 5 Nov or Feb print that the single-fee migration is (or will be) accretive to take rate or revenue in 4Q26 or FY27, with a number or a direction ("higher take rate")?
- **type:** binary (risk to the short; carries a `## 9. Impact` table)
- **resolution date:** ~2027-02-11 (4Q26 letter and call); an earlier Yes at the 5 Nov print resolves it
- **registry entry:** `docs/pitch-forecasts/QUESTIONS.md` § R04
- **batch:** A10 (with R05, R07)

## Files

| path | contents |
|---|---|
| `research-log.md` | revision 1 research log (schema: forecast skill `references/research-log-format.md`) plus §9 Impact |
| `forecasts/2026-09-17-forecast.json` | binary `final`, estimates, conventions, `impact` block, sensitivity, monitoring |
| `datasets/r04_statement_record.csv` | the four prints since the migration began (3Q25–2Q26): forward take-rate sentence, driver named, whether it counts under the log's convention |
| `datasets/r04_driver_attribution_history.csv` | every letter's forward take-rate sentence 4Q22–2Q26 and the driver it names |
| `datasets/r04_decomposition.csv` | the letter-route / call-route / Feb-route arithmetic behind the decomposition estimate |
| `sources/` | Kalshi and Polymarket API JSON (2026-09-17T03:34:27Z), `web_queries_2026-09-17.md` (shared batch web log) |

## Headline (revision 1)

P(Yes) = **0.58**, credible interval 0.42–0.72 (P(Yes at 5 Nov) ≈ 0.39). Anchor: flat prior 0.50 (no market prices the statement). Base rate 0.61 (1.5 of 4 prints since the migration began made a qualifying attribution, over two prints); decomposition 0.57. Impact if Yes: FY27 revenue +$230M, FY27 margin +1.3pp, stock ≈ +$7/share; EV ≈ +$4.1/share — **material**.
