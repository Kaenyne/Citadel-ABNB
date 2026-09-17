# C08 — q3-revenue-fx-integer

- **id:** C08
- **title:** What year-over-year FX contribution to 3Q26 revenue growth will Airbnb state at the 5 Nov print?
- **type:** multiple choice — (a) ≥ +3 points, (b) +2, (c) ≤ +1, (d) not stated
- **resolution date:** 2026-11-05 (3Q26 shareholder letter, after market close)
- **registry entry:** `docs/pitch-forecasts/QUESTIONS.md` § C08
- **batch:** A05

## Files

| path | contents |
|---|---|
| `research-log.md` | revision 1 research log (schema: forecast skill `references/research-log-format.md`) |
| `forecasts/2026-09-17-forecast.json` | MC vector, estimates, sensitivity, monitoring |
| `datasets/c08_model.py` | basket rebuild on the FRED pull, spec points, letter-rounding Monte Carlo, sensitivities, guide track record; `py -3.13 docs/pitch-forecasts/questions/q3-revenue-fx-integer/datasets/c08_model.py` from the repo root |
| `datasets/c08_basket_rebuild.csv` | revenue-weighted basket 1Q26–3Q26 on FRED through 2026-09-11 (QTD and spot-held), against the published 4 Sep vintage |
| `datasets/c08_spec_points.csv` | every live 3Q26 revenue-FX construction and the integer it implies |
| `datasets/c08_integer_mc.csv`, `c08_sensitivity.csv` | component and mixture probabilities; 12 single-assumption reruns |
| `datasets/c08_guide_track_record.csv` | management's guided FX language vs the printed integer, 3Q23–2Q26 (n 10), verbatim quotes |
| `sources/` | FRED daily pull (ten series through 2026-09-11) with fetch manifest; web query log with URLs and timestamps |

## Headline (revision 1)

(a) ≥ +3: **0.50**; (b) +2: **0.30**; (c) ≤ +1: **0.18**; (d) not stated: **0.02**. Anchor (the programme's registered fx-lag-v2 H2 point, +1.85 → P(≥3) 0.28); final − anchor +22 points on (a), justified by management's guided-vs-printed record (9 of 10 pairs printed at or above the guided figure; both "approximately three" guides printed 3 and 4) and by the lag-loaded kernel reproducing the guide at +2.9 on the refreshed basket.
