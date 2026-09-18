# S03 — close-12feb-2027

- **id:** S03
- **title:** What will ABNB's closing price be on the first trading session after the 4Q26 print (expected 12 Feb 2027)?
- **type:** continuous (USD); percentile table plus P(≤ $150), P(≤ $143), P(≥ $180)
- **resolution date:** ~2027-02-12 (first session after the 4Q26 release; the release is expected 11 Feb 2027 after the close)
- **registry entry:** `docs/pitch-forecasts/QUESTIONS.md` § S03
- **batch:** A07 (model shared with S02 `close-15dec-2026`; master scripts live there)

## Files

| path | contents |
|---|---|
| `research-log.md` | revision 1 research log (claims 20–25 here; claims 1–19 reused from the S02 log) |
| `forecasts/2026-09-17-forecast.json` | continuous `final` percentiles, `threshold_probs`, estimates, the Feb-print event block, sensitivity, monitoring |
| `datasets/run.py` | wrapper: re-runs `../close-15dec-2026/datasets/abnb_path_mixture.py` and `final_blend.py`, copies the S03 outputs here |
| `datasets/mixture_base_run.json`, `sensitivity.csv`, `final_blend.json`, `S03_final_cdf.csv`, `S03_hist.csv` | model outputs (copies of the S02 run) |
| `datasets/implied_dist_20260917T031221Z.json`, `implied_term_structure_20260917T031221Z.csv` | own-IV term structure and the Jan/Mar-interpolated smile RND at 12 Feb |
| `sources/` | yfinance history, option chain (10 expiries), expiries, ^IRX, calendar; web analyst-action capture |

## Headline (revision 1)

Median **$165** (5–95% **$113–242**); P(≤ $150) **0.34**, P(≤ $143) **0.27**, P(≥ $180) **0.35**. Anchor: Jan/Mar-interpolated options smile RND, median $167.4 risk-neutral ($169.5 drift-shifted), 0.33 / 0.27 / 0.38. The decomposition alone gives $163. The February print's own event is carried at a +2 to +4% mean (5 of 6 Q4 prints positive, shrunk), which offsets most of the team's negative 5 Nov view by February.
