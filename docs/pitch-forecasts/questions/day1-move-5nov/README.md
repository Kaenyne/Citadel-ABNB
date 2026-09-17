# S01 — day1-move-5nov

- **id:** S01
- **title:** What will ABNB's close-to-close return be on the first trading session after the 3Q26 print?
- **type:** continuous (percent, −40 to +40), percentile table plus P(≤ −8%), P(≤ −5%), P(≥ +5%), P(≥ +10%); the team's base-case conditional distribution reported separately
- **resolution date:** 2026-11-06 (close on the first session after the 5 Nov 2026 release ÷ close on the release day − 1)
- **registry entry:** `docs/pitch-forecasts/QUESTIONS.md` § S01
- **batch:** A06

## Files

| path | contents |
|---|---|
| `research-log.md` | revision 1 research log (schema: forecast skill `references/research-log-format.md`) |
| `forecasts/2026-09-17-forecast.json` | continuous `final` block, `threshold_probs`, `conditional_base_case`, `conditional_thesis_breaker`, print-state probabilities, estimates, sensitivity, monitoring |
| `datasets/s01_mixture.py` | the mixture (numpy/pandas only, seed 20260917, n 400,000); `py -3.13 docs/pitch-forecasts/questions/day1-move-5nov/datasets/s01_mixture.py` from the repo root |
| `datasets/s01_cells.csv` | reaction-panel cells (print sign × guide vs Street × nights-guide direction) with n, mean, median, sd, prints |
| `datasets/s01_estimates.csv` | the three estimates and the final mixture: percentiles, sd, rms, threshold probabilities |
| `datasets/s01_percentiles.csv`, `s01_thresholds.csv` | the headline table and the threshold probabilities |
| `datasets/s01_conditional_base_case.csv` | model-only, empirical-cell and blended conditional distributions for the base case |
| `datasets/s01_sensitivity.csv` | 21 single-assumption reruns (nowcast centre/sd, S1/S2 weight, positioning term, residual sd, guide gap, mixture weights, options sd) |
| `datasets/s01_components.json` | every parameter, state probability and summary the log quotes |
| `datasets/pull_options.py`, `options_event_sd.py` | fresh yfinance chain pull and the event-sd computation (Black-76 on parity forwards, quadratic smile, pre/post-print pairs and LS); outputs `options_term_structure.csv`, `options_event_sd.csv` |
| `sources/` | yfinance chain + meta + price history (2026-09-17T03:09Z), Kalshi KXABNB / KXABNBA and Polymarket search JSON (03:09Z), Airbnb IR events page fetch (03:13Z); UTC time in each filename |

## Headline (revision 1)

Unconditional day-1 close-to-close return: **p5 −17.4 / p10 −14.3 / p25 −9.2 / p50 −2.9 / p75 +3.3 / p90 +9.9 / p95 +14.0** (%), mean −2.7, sd 9.5. **P(≤ −8%) 0.29, P(≤ −5%) 0.41, P(≥ +5%) 0.20, P(≥ +10%) 0.10**; P(< 0) 0.62. Bound mass 0.1% each side.

Team base case (decelerating print, guide below Street, bucket downgraded; unconditional weight ≈ 0.50): **median −8.6%**, p5 −20.2 / p95 +4.2, **P(≤ −8%) 0.53**, P(< 0) 0.87. Thesis-breaker cell (accelerating print, guide at/above Street; weight ≈ 0.08): median +5.0%, P(≥ +5%) 0.50.

Anchor: options-implied event sd 9.0% (fresh chain 17 Sep; 8.0–9.5 across specs; B note 9.5%) with no directional content; the mixture's sd 9.5 sits inside the options noise band, so the location (−2.9 median, 62% down) is the repo's claim and the width is the market's.
