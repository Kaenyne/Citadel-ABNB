# B12 — bonus-fy27-investment-year

At the Feb 2027 print, will management guide FY27 adjusted EBITDA margin down year over year versus FY26 actual (floor/point below the FY26 reported margin), or explicitly frame 2027 as an investment year with margin below FY26? Binary; resolves ~11 Feb 2027.

Revision 1 (17 Sep 2026, Fable, batch A17): **P = 0.50, CI 0.38–0.62** under the literal reading (any floor strictly below the one-decimal FY26 print, or explicit down/investment-year language); **0.38 (0.27–0.50)** under the material reading (floor ≥ 50bp below the print, the FY24/FY25 haircut form, or explicit language). Two of the five Februaries since 2022 set a numeric floor 184–190bp below the print; three said "in-line"/"maintain"/"stable"; the words "down"/"lower" have never been used for a full year. Built on F03's model and regime weights unchanged; the material reading equals F03's option (d) (0.38). Impact if Yes: FY27 margin −0.3pp vs the team's line build, −0.9pp vs the Street; FY27 EPS −$0.20 on the Street number; stock ≈ −$5/share (−$2 to −$9 by gap size); EV ≈ −$2.5/share, material.

- `research-log.md` — the log, with `## 9. Impact`.
- `forecasts/2026-09-17-forecast.json` — the forecast in the brief's schema (both readings).
- `datasets/b12_model.py` → `b12_sensitivity.csv` (numpy, seed 20260917, ~5 s: `py -3.13 docs/pitch-forecasts/questions/bonus-fy27-investment-year/datasets/b12_model.py`); `datasets/feb_fy_margin_sentences.csv` — the five February FY margin sentences verbatim.
- `sources/` — Polymarket snapshot (2026-09-17T08:27:05Z) and the web-search log.
