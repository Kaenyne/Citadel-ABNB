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
| `research-log.md` | revision 2 research log (schema: forecast skill `references/research-log-format.md`); section 10 lists every change against audit A06 |
| `forecasts/2026-09-17-forecast.json` | revision 2: continuous `final` block, `threshold_probs`, `conditional_base_case` (three gates), `conditional_thesis_breaker`, `other_cells`, print-state probabilities, estimates (incl. the audit's independent number), sensitivity, monitoring |
| `datasets/s01_joint_v2.py` | **revision-2 model**: one joint draw over print state × C01 × C02 × latent signal flag × return (numpy/pandas/scipy/sklearn, seed 20260917, n 600,000); `py -3.13 docs/pitch-forecasts/questions/day1-move-5nov/datasets/s01_joint_v2.py` from the repo root |
| `datasets/s01_v2_windows.csv` | S1 / S2 reaction-function refits on n16, W1 (2023Q1+) and W2 (2024Q1+) with residual sd and LOO R² |
| `datasets/s01_v2_estimates.csv` | base rate (history kernel), decomposition (model branch), anchor (options, symmetric; two-piece as a labelled judgement) and the final joint distribution |
| `datasets/s01_v2_percentiles.csv`, `s01_v2_thresholds.csv` | the revision-2 headline table and threshold probabilities |
| `datasets/s01_v2_cells.csv`, `s01_v2_conditionals.csv` | the twelve joint cells (state × C01 × C02) and the named conditionals (base case, breaker, R01 Yes/No, …), all from the same draw |
| `datasets/s01_v2_sensitivity.csv` | 36 single-assumption reruns of the joint model (states, κ, S1 window, S2 weight, positioning, C02 effect and dependence, C01, residual, options sd, QQQ) |
| `datasets/s01_v2_slider.csv`, `s01_v2_components.json` | fitted three-Gaussian slider approximation (max CDF error stated); every parameter, state probability, cell and summary the log quotes; Astra's replayed distribution |
| `datasets/s01_mixture.py` | revision-1 mixture, superseded, kept as the audit trail (numpy/pandas only, seed 20260917, n 400,000); `py -3.13 docs/pitch-forecasts/questions/day1-move-5nov/datasets/s01_mixture.py` from the repo root |
| `datasets/s01_cells.csv` | reaction-panel cells (print sign × guide vs Street × nights-guide direction) with n, mean, median, sd, prints |
| `datasets/s01_estimates.csv` | the three estimates and the final mixture: percentiles, sd, rms, threshold probabilities |
| `datasets/s01_percentiles.csv`, `s01_thresholds.csv` | the headline table and the threshold probabilities |
| `datasets/s01_conditional_base_case.csv` | model-only, empirical-cell and blended conditional distributions for the base case |
| `datasets/s01_sensitivity.csv` | 21 single-assumption reruns (nowcast centre/sd, S1/S2 weight, positioning term, residual sd, guide gap, mixture weights, options sd) |
| `datasets/s01_components.json` | every parameter, state probability and summary the log quotes |
| `datasets/pull_options.py`, `options_event_sd.py` | fresh yfinance chain pull and the event-sd computation (Black-76 on parity forwards, quadratic smile, pre/post-print pairs and LS); outputs `options_term_structure.csv`, `options_event_sd.csv` |
| `sources/` | yfinance chain + meta + price history (2026-09-17T03:09Z), Kalshi KXABNB / KXABNBA and Polymarket search JSON (03:09Z), Airbnb IR events page fetch (03:13Z); UTC time in each filename |

## Headline (revision 2, after audit A06)

Unconditional day-1 close-to-close return: **p5 −17.1 / p10 −13.9 / p25 −8.6 / p50 −2.1 / p75 +4.2 / p90 +10.7 / p95 +14.5** (%), mean −2.0, sd 9.8 (interior 9.55). **P(≤ −8%) 0.27, P(≤ −5%) 0.38, P(≥ +5%) 0.22, P(≥ +10%) 0.11**; P(< 0) 0.59; P(|r| ≥ 15%) 0.125. Bound mass 0.14% below / 0.11% above (0.1% explicit each side).

Team base case (decelerating print AND guide below Street AND bucket downgraded, three gates generated jointly; **probability 0.36**): **median −5.1%**, p5 −19.2 / p95 +12.6, **P(≤ −8%) 0.37**, P(< 0) 0.71. Thesis-breaker cell (accelerating print, guide at/above Street; probability 0.11): median +2.9%, P(≥ +5%) 0.40.

Anchor: options-implied event sd 9.0% (fresh chain 17 Sep; 8.0–9.5 across specs; B note 9.5%), symmetric; the location (−2.1 median, 59% down) is the repo's claim (the pre-stated sign rule, which survives W1 and W2, given the run's adopted print states from R01/R02), the width is the market's. Astra's independent distribution: median −2.2, P(≤ −8) 0.25, base case median −4.2 / P(< 0) 0.70.

Revision 1 (superseded): p50 −2.9, P(≤ −8) 0.29; base case at p 0.50 with median −8.6 and P(< 0) 0.87 — withdrawn (two gates, conditional not derived from the published mixture; audit A06-01/02).
