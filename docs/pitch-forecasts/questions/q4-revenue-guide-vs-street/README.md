# C01 — q4-revenue-guide-vs-street

- **id:** C01
- **title:** Will Airbnb's 4Q26 revenue guidance midpoint, given at the 5 Nov print, be below the Street's 4Q26 revenue consensus mean?
- **type:** binary, plus a continuous forecast of the guidance midpoint (USD millions, percentile table)
- **resolution date:** 2026-11-05 (3Q26 shareholder letter, after market close); Street value recorded 2026-11-04
- **registry entry:** `docs/pitch-forecasts/QUESTIONS.md` § C01
- **batch:** A01

## Files

| path | contents |
|---|---|
| `research-log.md` | revision 1 research log (schema: forecast skill `references/research-log-format.md`) |
| `forecasts/2026-09-17-forecast.json` | binary `final` + `continuous` percentile block, estimates, sensitivity, monitoring |
| `datasets/c01_model.py` | the Monte Carlo (numpy/pandas only, seeded); `py -3.13 docs/pitch-forecasts/questions/q4-revenue-guide-vs-street/datasets/c01_model.py` from the repo root |
| `datasets/c01_mc_summary.csv`, `c01_percentiles.csv`, `c01_guide_hist.csv` | base-case outputs |
| `datasets/c01_final_mixture.csv`, `c01_final_mixture_hist.csv` | the final mixture that the JSON quotes |
| `datasets/c01_sensitivity.csv` | 27 single-assumption reruns, including two B2-replication rows |
| `datasets/c01_base_rates.csv` | guide-vs-Street reference classes recomputed from the reaction panel |
| `datasets/street_drift_dolthub.csv` | Street next-quarter consensus drift, 50 days before each print to the last Sunday before it |
| `datasets/kalshi_q3_nights_implied.csv` | Kalshi KXABNB Q3 2026 nights strikes, mid prices, implied median |
| `sources/` | Polymarket and Kalshi API JSON, yfinance captures (price, LSEG-family revenue estimate), StockAnalysis fetch attempt; UTC fetch time in each filename |

## Headline (revision 1)

P(midpoint < LSEG-family 4Q26 mean on 4 Nov) = **0.75**, credible interval 0.62–0.85. Guide midpoint median **$3,100M**, 5–95% **$2,960–3,250M**. "Guide surprise" object P(midpoint < Street mean less the trailing-8 cushion, i.e. < ~$3,102M) = **0.51**. Anchor (Kalshi-implied 3Q26 nights pushed through the kernel) 0.68; the programme's previously published number (B2, 11 Sep) was 0.49 on a stacked-baseline GBV that sits $670M above the team's nowcast.
