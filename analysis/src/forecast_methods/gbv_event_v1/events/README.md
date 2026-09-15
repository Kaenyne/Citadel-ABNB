# GE-EVENT: earnings guide comparisons and daily price legs

15 September 2026. This plan supplements `GE_PREREG_v1.md` before the new event calculations. The historical events have previously been studied; no output is a fresh confirmatory discovery.

Primary expectation selection is the original L0 `PG-<target>-revenue` row, explicit `role=pre_guide`, finite value, `pit_usable=True`, `vendor_attributed=True`, and a named vendor (excluding unattributed/unknown). Date-only same-day rows rely on the documented morning-of-print convention. Raw timestamps are preserved: explicit timezone-aware instants must strictly precede 16:00 New York; naive, exact-close and post-close instants fail. Missing/quarantined rows stay missing. DoltHub is a separate, uniformly selected sensitivity: latest explicit DoltHub revenue snapshot strictly before the event, never an automatic primary fallback. It is a separately labelled mirror, not a newly independent source family.

The implied-guide comparator divides revenue consensus by one plus the trailing-eight median revenue/first-guide cushion, with at least three realised observations whose actual-revenue publication date is strictly BEFORE the event. Current-print actual revenue is excluded from that cushion. Both published-guide comparisons become known only after release. Neither measures observed expectations for management's guide.

Outcomes are ABNB minus QQQ simple returns on matching dates. Gap, first regular session and close-to-close are calculated directly from daily prices. The exact identity compounds each security's gap and session before differencing; excess returns themselves must not be compounded together. Five/twenty-session open-entry returns are separate secondary horizons. Daily OHLC does not reveal during-call moves, wick ordering or stop execution.

Use all 23 frozen earnings events. Primary statistics include all eligible rows, plus W1/W2 sensitivity slices by PRINT quarter (2023Q1+ / 2024Q1+; nested). The event slices are explicitly distinct from the forecast agent's target-quarter windows. Holm correction covers all twelve primary contrasts: two comparisons by two price legs by all/W1/W2. Pearson two-sided permutation p uses 19,999 fixed-seed permutations with a plus-one correction; it assumes exchangeability and is descriptive at this n. Pearson Fisher intervals and HC1 slope intervals using t(n-2) critical values are approximate. Spearman and its asymptotic p are descriptive, outside the primary claim. No slope or threshold search. Current-print revenue surprise is the only optional control (original attributed at-print row), reported on the same matched rows. Leave-one-event/year analyses record all omissions, not only influential cases.

The optional earlier-origin forecast join uses the frozen candidate's origin date and guide target. Consensus at that origin is selected independently from explicit DoltHub snapshots strictly before the origin; event-morning consensus must never be treated as known at the earlier origin. This join remains reconstructed research, and cannot alone promote a strategy. Because the candidate guide and Street implied guide share the same cushion divisor, their ratio equals candidate revenue divided by origin Street revenue: the cushion cancels. This is revenue disagreement on a hypothetical common guide basis, not independent guide-expectation evidence. Origin-close to next-open/next-close returns include the intervening position exposure. The expanded historical set ends at the Q3 2026 guide (13/11 W1/W2 target events); separately labelled frozen windows end at Q2 2026 (12/10), matching the forecast audit. No transaction-cost-adjusted strategy is inferred from ex-post guide labels.

Canonical completed outputs are in `data/processed/forecast_methods/gbv_event_v1/events_v1/run_v3/`. The first failed adapter attempt is preserved in `run_v1/ATTEMPT_FAILURE.json`; `run_v2/` is the successful pre-hardening version. The final run leaves primary numerical tables unchanged and adds timestamp provenance and supplementary forecast-window/influence tables. See `docs/revenue-forecast-strategy/05_backtests/GE_EVENT_RESULTS_v1.md` for results and interpretation.

Run from the worktree root with the project Python:

```powershell
python -B analysis/src/forecast_methods/gbv_event_v1/events/run.py --out data/processed/forecast_methods/gbv_event_v1/events_v1/run_replay_v1
python -B -m pytest analysis/src/forecast_methods/gbv_event_v1/events/test_events.py -q
```

The output directory must be new. A fresh `--out` path reproduces without overwriting anything. The package writes no registry, scorer, shared model or existing source file.
