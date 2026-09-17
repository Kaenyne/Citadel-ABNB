# F03 — fy27-margin-guide

What FY27 adjusted EBITDA margin guidance will Airbnb give in the 4Q26 shareholder letter (~11 Feb 2027)? Multiple choice: (a) ≥36.5 / (b) 36.0–36.4 / (c) 35.5–35.9 / (d) <35.5, down y/y or investment-year / (e) none.

- Forecast (revision 1, 2026-09-17): **(a) 0.08, (b) 0.17, (c) 0.27, (d) 0.38, (e) 0.10**. Leading option (d), credible range 0.28–0.58. Anchor: the repo's WS05/H12 prior (floor = FY26 print − 0 to 190bp) → P(d) 0.55; |final − anchor| 17 points.
- Convention: qualitative flat sentences ("stable", "maintain") map to the bucket of the FY26 reported margin; under the strict reading (all qualitative → e) the vector is a 0.02 / b 0.05 / c 0.10 / d 0.36 / e 0.48.
- Files: `research-log.md`, `forecasts/2026-09-17-forecast.json`, `datasets/f03_model.py` (numpy, seed 20260917), `datasets/f03_sensitivity.csv`, `feb_letter_guides_4Q20-4Q25.csv`, `sources/` (market JSON, web query log).
- Batch A08 with F01, F02, F04 (F04 is conditioned on this vector).
