# B10 — bonus-interest-income-falls

- **id:** B10
- **title:** Will 4Q26 interest income be ≤ 90% of 4Q25's (≤ $145.8M on the printed $162M)?
- **type:** binary (bonus for the short; carries a `## 9. Impact` table)
- **resolution date:** ~2027-02-11 (4Q26 release / FY26 10-K)
- **registry entry:** `docs/pitch-forecasts/QUESTIONS.md` § B10
- **batch:** A16 (with B08, B09, B17)

## Files

| path | contents |
|---|---|
| `research-log.md` | revision 1 research log (schema: forecast skill `references/research-log-format.md`) plus §9 Impact and the extreme-probability audit |
| `forecasts/2026-09-17-forecast.json` | binary `final`, companion probabilities, estimates, model, `impact` block, sensitivity, monitoring |
| `datasets/b10_model.py` | the model (numpy/pandas only, seeded); `py -3.13 docs/pitch-forecasts/questions/bonus-interest-income-falls/datasets/b10_model.py` from the repo root |
| `datasets/b10_results.csv` | M7-rule Monte Carlo, sensitivities and the scenario mixture |
| `datasets/b10_history.csv` | interest income, T-bill, earning base and realised yield β by quarter 1Q24–2Q26 |
| `sources/` | FRED DTB3 / DGS1 / DFEDTARU CSVs (2026-09-17T08:20:52Z), Kalshi KXFEDDECISION and KXFED JSON, Polymarket Fed and Airbnb searches (2026-09-17T08:21:21Z), `web_queries_2026-09-17.md` (shared batch web log) |

## Headline (revision 1)

P(Yes) = **0.05**, credible interval 0.02–0.10. The Fed hiked on 16 Sep and Kalshi prices a second hike by December at 0.69, so the 4Q26 T-bill runs +9–13% y/y while the earning base grows ~6%; the M7 rule puts 4Q26 interest income at ~$177M (+9%), and the threshold needs a −18% miss. The only routes to Yes are a ≥ $3bn buyback cash draw or an emergency easing cycle. Anchor: M7's registered pre-hike band → 0.11. Impact if Yes: FY27 EPS −$0.13, stock ≈ −$2; EV ≈ −$0.1/share — **immaterial**, drop from the memo.
