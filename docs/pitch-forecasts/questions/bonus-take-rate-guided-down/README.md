# B17 — bonus-take-rate-guided-down

- **id:** B17
- **title:** At the 5 Nov print, will management guide 4Q26 or FY27 take rate lower (any statement that take rate will be down y/y, or that incentives/new businesses will reduce it)?
- **type:** binary (bonus for the short; carries a `## 9. Impact` table)
- **resolution date:** 2026-11-05 (3Q26 release and call)
- **registry entry:** `docs/pitch-forecasts/QUESTIONS.md` § B17
- **batch:** A16 (with B08, B09, B10); mirror of R04 `risk-single-fee-take-rate-accretion-stated`

## Files

| path | contents |
|---|---|
| `research-log.md` | revision 1 research log (schema: forecast skill `references/research-log-format.md`) plus §9 Impact; six resolution conventions stated in §0b |
| `forecasts/2026-09-17-forecast.json` | binary `final`, companion route probabilities and the strict-convention number, estimates, model, `impact` block, sensitivity, monitoring |
| `datasets/b17_model.py` | the model (numpy/pandas only, seeded); `py -3.13 docs/pitch-forecasts/questions/bonus-take-rate-guided-down/datasets/b17_model.py` from the repo root |
| `datasets/b17_results.csv` | 4Q26 take-rate arithmetic (team, Street, RNPL pull-forward cases), route union, sensitivities, base rates |
| `sources/` | Kalshi and Polymarket API JSON (2026-09-17T08:21:21Z), `web_queries_2026-09-17.md` (shared batch web log incl. the Skift pilot fetch) |

## Headline (revision 1)

P(Yes) = **0.42**, credible interval 0.28–0.56 (strict convention, FY26 wording excluded: 0.33). The letter has said "lower" once in 13 prints, and the 4Q25 comp is easy (team and Street have 4Q26 take rate up 13–21bp), so the letter route is only ~0.12; the Yes mass comes from the CFO repeating the 2Q26 form ("relatively flat … accounting for … higher customer incentives related to new businesses") with the direct-link pilot (6–10% host fee, 29–31 Aug) making a take-rate question near-certain. Anchor: flat prior 0.50. Impact if Yes: 4Q26 revenue −$30M, FY27 −$170M, FY27 margin −1.0pp, EPS −$0.21, stock ≈ −$6; EV ≈ −$2.5/share — **material**.
