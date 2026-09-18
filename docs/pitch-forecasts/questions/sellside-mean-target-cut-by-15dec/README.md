# S04 — sellside-mean-target-cut-by-15dec

- **id:** S04
- **title:** Will the mean sell-side 12-month price target for ABNB on 15 Dec 2026 be at least $5 below its 12 Sep 2026 level ($181.8, 32 targets)?
- **type:** binary
- **resolution date:** 2026-12-15 (mean of live targets, feed convention of `data/processed/reverse_dcf/D/`, 365-day window; threshold ≤ $176.80)
- **registry entry:** `docs/pitch-forecasts/QUESTIONS.md` § S04
- **batch:** A07 (price paths from the S02 model in `../close-15dec-2026/datasets/`)

## Files

| path | contents |
|---|---|
| `research-log.md` | revision 1 research log (claims 26–33 here; claims 1–19 reused from the S02 log) |
| `forecasts/2026-09-17-forecast.json` | binary `final` with interval, estimates, resolution inputs, model outputs, sensitivity, monitoring |
| `datasets/target_base_rates.py` | base rates from the daily mean-target panel, print-centred windows, the window regression, the live tape recomputed from the fresh feed, known price lags → `target_base_rates.json`, `target_change_print_windows.csv` |
| `datasets/run.py` | wrapper: re-runs the S02 mixture (S04 block) and the base rates, copies `mixture_base_run.json` and `sensitivity.csv` here |
| `sources/` | yfinance upgrades/downgrades feed (469 rows), analyst price targets, info subset (targetMeanPrice), recommendations, history, calendar; web analyst-action capture (Morgan Stanley $170 initiation, weekly table) |

## Headline (revision 1)

P(Yes) = **0.29** (0.20–0.40). Base rates 0.18–0.27 (63-session and print-centred windows of the tape); tape-lag decomposition 0.30 on a $183.22 base (Morgan Stanley re-initiated at $170 from $125 on 16 Sep, so the required cut is 3.5%); anchor 0.50 (the D note's 12 Sep "base case cut" judgement, which omitted the August rally's lag-2 term). Conditional on the team's base 5 Nov branch: 0.38; on an accelerating print: 0.15.
