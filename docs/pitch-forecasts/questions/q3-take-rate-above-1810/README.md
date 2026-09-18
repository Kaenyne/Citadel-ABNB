# C11 — q3-take-rate-above-1810

- **id:** C11
- **title:** Will Airbnb's printed 3Q26 take rate (revenue ÷ GBV, as reported) be ≥ 18.10%?
- **type:** binary (with the GBV-conditional table required by the fine print)
- **resolution date:** 2026-11-05 (3Q26 press release / shareholder letter, after market close)
- **registry entry:** `docs/pitch-forecasts/QUESTIONS.md` § C11
- **batch:** A05

## Files

| path | contents |
|---|---|
| `research-log.md` | revision 1 research log (schema: forecast skill `references/research-log-format.md`) |
| `forecasts/2026-09-17-forecast.json` | binary `final` + GBV-conditional table, estimates, sensitivity, monitoring |
| `datasets/c11_model.py` | joint Monte Carlo (numpy/pandas only, seeded); `py -3.13 docs/pitch-forecasts/questions/q3-take-rate-above-1810/datasets/c11_model.py` from the repo root |
| `datasets/c11_mc_summary.csv` | team-band base case |
| `datasets/c11_by_gbv_band.csv` | P(≥18.10 \| GBV band) from the final mixture, plus point-GBV rows |
| `datasets/c11_sensitivity.csv` | 22 single-assumption reruns incl. the B1 replication row |
| `datasets/c11_history.csv` | printed Q3 take rates 3Q21–3Q25 with the revenue-minus-GBV FX wedge |
| `sources/` | Kalshi KXABNB / KXABNBA JSON, Polymarket searches (UTC fetch time in each filename); web query log |

## Headline (revision 1)

P(3Q26 take rate ≥ 18.10%) = **0.55**, credible interval 0.40–0.70. Conditional: at printed GBV ≤ $26.2bn ≈ 0.95; $26.3–26.5bn ≈ 0.75; ≥ $26.6bn ≈ 0.15. Anchor: the Street's own means (LSEG revenue 4,744.9 / MODL GBV 26,375 = 17.99%) → 0.45; B1's published 0.53 is reproduced under B1's inputs. The question is the printed GBV, not the fee.
