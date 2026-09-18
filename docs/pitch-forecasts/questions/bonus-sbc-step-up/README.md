# B09 — bonus-sbc-step-up

- **id:** B09
- **title:** Will 4Q26 stock-based compensation be ≥ $500M?
- **type:** binary (bonus for the short; carries a `## 9. Impact` table)
- **resolution date:** ~2027-02-11 (4Q26 release)
- **registry entry:** `docs/pitch-forecasts/QUESTIONS.md` § B09
- **batch:** A16 (with B08, B10, B17)

## Files

| path | contents |
|---|---|
| `research-log.md` | revision 1 research log (schema: forecast skill `references/research-log-format.md`) plus §9 Impact |
| `forecasts/2026-09-17-forecast.json` | binary `final`, companion probabilities, estimates, model, `impact` block, sensitivity, monitoring |
| `datasets/b09_model.py` | the model (numpy/pandas only, seeded); `py -3.13 docs/pitch-forecasts/questions/bonus-sbc-step-up/datasets/b09_model.py` from the repo root |
| `datasets/b09_results.csv` | the three routes (Q4/Q2 seasonal, y/y rule, FY26-sentence) and sensitivities |
| `datasets/b09_history.csv` | quarterly SBC 1Q22–2Q26 from the release reconciliation tables, y/y and Q4/Q2 ratios |
| `sources/` | Kalshi and Polymarket API JSON (2026-09-17T08:21:21Z), `web_queries_2026-09-17.md` (shared batch web log) |

## Headline (revision 1)

P(4Q26 SBC ≥ $500M) = **0.10**, credible interval 0.05–0.20. Note: the releases print 4Q25 SBC at **$411M** (not the registry's $400M; FY25 $1,592M = 358 + 424 + 399 + 411), so the needed y/y is +21.7%; Q4 has printed 0.954–0.969 × Q2 in each of 2023–25, which on 2Q26's $487M gives ~$468M. Anchor: M7 rule $465M with its h=2 error pool → 0.16. Impact if Yes: no margin effect; FY27 GAAP EPS −$0.20; stock ≈ −$3; EV ≈ −$0.3/share — **immaterial**, drop from the memo.
