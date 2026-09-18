# F02 — q1-27-revenue-guide-growth

What y/y growth will the midpoint of Airbnb's 1Q27 revenue guidance (4Q26 letter, ~11 Feb 2027) imply on 1Q26's $2,678M? Continuous, percent.

- Forecast (revision 1, 2026-09-17): median **+9.4%** (guide midpoint ≈ $2,930M); 5/10/25/50/75/90/95 = 3.6 / 4.9 / 7.0 / 9.4 / 12.0 / 14.3 / 15.6; **P(<10%) 0.56, P(<9.4%) 0.48, P(≥12%) 0.25**.
- Anchor: LSEG 1Q27 mean $3,010M (+12.4%, n 21, Aug vintage); gap-adjusted +11.0%. Pre-registered INT-20 ($2,930–2,990M) spans the p50–p70.
- Files: `research-log.md` (the audit trail), `forecasts/2026-09-17-forecast.json`, `datasets/f02_model.py` and `f02_final_mixture.py` (numpy, seed 20260917; run in that order from this folder), `datasets/*.csv` (outputs, ledger extract, λ table), `sources/` (Kalshi/Polymarket JSON, web query log).
- Batch A08 with F01, F03, F04.
