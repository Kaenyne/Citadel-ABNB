# S02 — close-15dec-2026

- **id:** S02
- **title:** What will ABNB's closing price be on 15 Dec 2026?
- **type:** continuous (USD); percentile table plus P(≤ $150), P(≤ $143), P(≥ $180)
- **resolution date:** 2026-12-15 (Nasdaq close)
- **registry entry:** `docs/pitch-forecasts/QUESTIONS.md` § S02
- **batch:** A07 (with S03 `close-12feb-2027` and S04 `sellside-mean-target-cut-by-15dec`; this folder holds the shared model)

## Files

| path | contents |
|---|---|
| `research-log.md` | revision 1 research log (schema: forecast skill `references/research-log-format.md`) |
| `forecasts/2026-09-17-forecast.json` | continuous `final` percentiles, `threshold_probs`, estimates, day-1 mixture used, sensitivity, monitoring |
| `datasets/pull_yfinance.py` | yfinance capture of price history, option chains, analyst targets, feed actions (writes to `sources/`) |
| `datasets/implied_dist.py` | own Black-76 IVs, smile fits, event sd, smile RND at 15 Dec and 12 Feb → `implied_term_structure_*.csv`, `implied_dist_*.json` |
| `datasets/abnb_path_mixture.py` | the seeded Monte Carlo (seed 20260917, n 400,000) for S02, S03 and S04 → `mixture_base_run.json`, `sensitivity.csv`, `S02_hist.csv`, `S03_hist.csv` |
| `datasets/final_blend.py` | CDF mixture of the decomposition and the drift-shifted options anchor → `final_blend.json`, `S02_final_cdf.csv`, `S03_final_cdf.csv` |
| `datasets/abnb_close_merged_to_20260916.csv` | daily closes (repo file to 4 Sep + yfinance after) used for the realised-vol and horizon base rates |
| `sources/` | yfinance captures (history, chains, expiries, targets, upgrades/downgrades, calendar, recommendations, info), Kalshi and Polymarket API JSON, web analyst-action capture; UTC fetch time in each filename |

Run order from the repo root: `py -3.13 .../datasets/pull_yfinance.py`, `implied_dist.py`, `abnb_path_mixture.py`, `final_blend.py`.

## Headline (revision 1)

Median **$162** (5–95% **$121–217**); P(≤ $150) **0.33**, P(≤ $143) **0.24**, P(≥ $180) **0.28**. Anchor: options-implied smile RND for 15 Dec, median $167.3 risk-neutral ($168.6 drift-shifted), 0.28 / 0.21 / 0.34. The decomposition alone gives a $159 median; the final is a 0.65/0.35 CDF blend. The memo's $143 is the 24th percentile of the 15 Dec close, not the base case.
