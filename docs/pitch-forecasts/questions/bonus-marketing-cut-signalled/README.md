# B03 — bonus-marketing-cut-signalled

- **id:** B03
- **title:** At the 5 Nov print, will management state that 4Q26 or FY27 marketing/S&M spend will grow more slowly than revenue, be "moderated", "optimised" or reduced, or quantify a reduction?
- **type:** binary (bonus item for the short; carries a `## 9. Impact` table); overlaps C04 (a) hold-and-cut and C09 (c) up
- **resolution date:** 2026-11-05 (3Q26 letter, prepared remarks and Q&A)
- **registry entry:** `docs/pitch-forecasts/QUESTIONS.md` § B03
- **batch:** A14 (with B01, B02)

## Files

| path | contents |
|---|---|
| `research-log.md` | revision 1 research log (schema: forecast skill `references/research-log-format.md`) plus §9 Impact; the decomposition is a stated four-path union (no script) |
| `forecasts/2026-09-17-forecast.json` | binary `final`, path split, conditionals on C04/C09, estimates, `impact` block, sensitivity, monitoring |
| `datasets/b03_marketing_statement_by_print.csv` | 23 prints 4Q20–2Q26: the forward marketing/S&M statement in the letter or call, verbatim or paraphrase, classified Yes/No with the reason |
| `datasets/b03_sm_history.csv` | S&M line 3Q24–2Q26 with y/y growth vs revenue growth |
| `sources/` | Polymarket and Kalshi API JSON (2026-09-17T08:03:45Z), `web_queries_2026-09-17.md` (batch web log) |

## Headline (revision 1)

P(a forward "marketing slower than revenue / moderated / reduced" statement at the 5 Nov print) = **0.18**, credible interval 0.10–0.30. Base rate 0.09 (4 of 23 prints, 1 of 18 since 1Q22, 0 of 10 since 1Q24, 0 of 5 Novembers); decomposition 0.26 (C09 "up" × marketing named 0.12; 2027 leverage Q&A 0.08; stated cut 0.05; resolver 0.04); anchor 0.20 (line build short-case sequence through C04). Impact if Yes: FY26 margin +1.2pp / FY27 +1.1pp on the cost side, 4Q26 nights −0.3pt, stock ≈ −$3 (sign uncertain); EV ≈ −$0.5/share — **immaterial as a stock line; carry as the tell that the floor is being defended with the growth budget**.
