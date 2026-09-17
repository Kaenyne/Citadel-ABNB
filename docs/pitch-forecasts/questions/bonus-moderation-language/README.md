# B01 — bonus-moderation-language

- **id:** B01
- **title:** At the 5 Nov print, will management use demand-softening language of the kind that preceded 8–13% declines ("moderation"/"moderate" applied to nights or demand, "shorter lead times", "softening", "macro uncertainty affecting bookings", or "deceleration" for 4Q26)?
- **type:** binary (bonus item for the short; carries a `## 9. Impact` table); overlaps C02 option (d)
- **resolution date:** 2026-11-05 (3Q26 letter and prepared remarks)
- **registry entry:** `docs/pitch-forecasts/QUESTIONS.md` § B01
- **batch:** A14 (with B02, B03)

## Files

| path | contents |
|---|---|
| `research-log.md` | revision 1 research log (schema: forecast skill `references/research-log-format.md`) plus §9 Impact |
| `forecasts/2026-09-17-forecast.json` | binary `final`, companion joints with C02 and the 3Q26 print branches, estimates, `impact` block, sensitivity, monitoring |
| `datasets/b01_letter_language_by_print.csv` | 16 letters 3Q22–2Q26: next-quarter nights descriptor, class, the verbatim softening phrase (or none), strict / with-synonym resolution, day-1 QQQ-excess |
| `datasets/b01_decomposition.py` | standard-library reproduction: base rates, C02-tree decomposition, branch and option conditionals, sensitivities, impact arithmetic; `py -3.13 docs/pitch-forecasts/questions/bonus-moderation-language/datasets/b01_decomposition.py` from the repo root |
| `datasets/b01_decomposition_output.csv` | every printed number |
| `sources/` | Polymarket and Kalshi API JSON (2026-09-17T08:03:45Z), `web_queries_2026-09-17.md` (batch web log) |

## Headline (revision 1)

P(softening language applied to forward demand at the 5 Nov print) = **0.34**, credible interval 0.24–0.46. Base rate 0.35 (6 of 16 letters strict, 8 of 16 with synonyms; 6 of 8 down-class descriptors carried the word, 0 of 8 others); decomposition 0.33 on C02's tree; anchor C02 (d) 0.31. Two-thirds of a Yes (0.21) is C02's directional "moderate" sentence. Impact: 3Q26 nights −0.6pt, 4Q26 −0.4pt, 4Q26 revenue −$22M, FY27 −$38M, stock −$4 vs the unconditional and ≈ 0 vs the memo base case; EV −$1.4/share vs unconditional — **not a separate memo line; the language marker of the base case**.
