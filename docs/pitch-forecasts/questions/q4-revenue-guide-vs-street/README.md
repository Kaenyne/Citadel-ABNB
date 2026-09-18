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
| `research-log.md` | revision 2 research log (schema: forecast skill `references/research-log-format.md`); §10 lists every change against the A01 audit |
| `forecasts/2026-09-17-forecast.json` | binary `final` + `continuous` percentile block, estimates, sensitivity, monitoring |
| `datasets/c01_model_v2.py` | the revision-2 Monte Carlo (numpy/pandas only, seeded); `py -3.13 docs/pitch-forecasts/questions/q4-revenue-guide-vs-street/datasets/c01_model_v2.py` from the repo root (~4 min); outputs `c01_v2_*.csv` (components, final mixture, bridge from B2, mixture-level sensitivities, weight sensitivity, Kalshi ladder distribution, register-gated base rates) |
| `datasets/c01_model.py` and `c01_*.csv` | the revision-1 model and outputs, kept unchanged as the audit trail (superseded) |
| `datasets/c01_mc_summary.csv`, `c01_percentiles.csv`, `c01_guide_hist.csv` | base-case outputs |
| `datasets/c01_final_mixture.csv`, `c01_final_mixture_hist.csv` | the final mixture that the JSON quotes |
| `datasets/c01_sensitivity.csv` | 27 single-assumption reruns, including two B2-replication rows |
| `datasets/c01_base_rates.csv` | guide-vs-Street reference classes recomputed from the reaction panel |
| `datasets/street_drift_dolthub.csv` | Zacks-mirror next-quarter consensus drift, last observation <= 50 days before each print to the last observation before it (proxy for LSEG drift scale only) |
| `datasets/kalshi_q3_nights_implied.csv` | Kalshi KXABNB Q3 2026 nights strikes, mid prices, implied median |
| `sources/` | Polymarket and Kalshi API JSON, yfinance captures (price, LSEG-family revenue estimate), StockAnalysis fetch attempt; UTC fetch time in each filename |

## Headline (revision 2, after audit A01)

P(midpoint < LSEG-family 4Q26 mean on 4 Nov) = **0.72**, credible interval 0.60–0.82 (revision 1: 0.75). Guide midpoint median **$3,100M**, 5–95% **$2,945–3,265M**. "Guide surprise" object P(midpoint < Street mean less the trailing-8 cushion, i.e. < ~$3,102M) = **0.51**. Anchor (Kalshi ladder shape pushed through the kernel, thin market) 0.67; the audit's independent analytic number (Astra) 0.62; the programme's previously published number (B2, 11 Sep) 0.49 on a stacked-baseline GBV that sits $670M above the team's nowcast. Audit: `docs/pitch-forecasts/audits/A01-research-audit.md`; response `A01-audit-response.md`.
