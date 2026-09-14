# ADR Q3 nowcast run: resume instructions if the session dies

Written 11 Sep 2026 at about 16:15 local, while two Fable agents (workstreams I and J) were paused on their own background python jobs. Everything below is on disk in this worktree (`C:\Users\krish\citadel-abnb-adrq3`, branch `krish/adr-q3-nowcast`). Read `docs/adrq3/BRIEF.md` for the question, rules and data map.

## State at the time of writing

**Background jobs (OS processes, keep running without any session):**
- `analysis/src/adrq3/I1_party_size_daily.py --shard k 8` for k = 0..7: party-size classification of review text over the Aug 2026 and 2025 reviews dumps, checkpointing per market into `data/processed/adrq3/I/cache/`. Progress was 50 of 246 market-vintages at 16:00. Log files under `data/processed/adrq3/I/logs/`.
- `analysis/src/adrq3/I2a_los_runs_dated.py --workers 3`: blocked-run lengths by stay date from the calendar files, writing per-file outputs to `data/processed/adrq3/I/los_runs/`. Progress was 121 of 189 files at 16:00.
- `analysis/src/adrq3/J1_calendar_price_yoy.py`: same-listing, same-forward-date listed-price y/y from the 2024-25 calendar vintages (log `data/processed/adrq3/J/J1_run.log`, coverage table `J1_price_coverage.csv` already written).
- `analysis/src/adrq3/J2_proxy_tests.py`: proxy backtests against the pricing residual (outputs `J2_*.csv` and `proxy_tests.csv` already present; it may have finished).

Check what is still running with:
```
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name like 'python%'\" | Where-Object { $_.CommandLine -match 'adrq3' } | Select-Object ProcessId, CommandLine"
```

**Already written (partial, from the pre-download or early file set):** I1 inventory and windows, I1 party-size quarterly, I3 geo mix (3Q26 value, history, backtest), I4 backtest scoreboard and series check; J adr_card_v2.csv, card_v2_backtest.csv, residual_nowcast.csv, J3 terms, error attribution and walk-forward paths (these J3 outputs were built with the H card's mix inputs because I's summary file did not exist yet).

## To finish workstream I (mix terms)
1. Wait for the eight I1 shards and I2a to exit. Every script is checkpointed; re-running a script skips finished units.
2. `py -3.13 analysis/src/adrq3/I1b_party_size_windows.py` (vintage-matched July-August party size and booked-capacity y/y by region; size term with the 0.59 coefficient).
3. `py -3.13 analysis/src/adrq3/I2b_los_windows.py` (run-length distribution Aug 2026 vs Sep 2025 for July-September stay dates, LOS term via 14a ratios and 14b bucket-share method).
4. `py -3.13 analysis/src/adrq3/I4_backtests.py` then `py -3.13 analysis/src/adrq3/I5_summary.py`, which writes `data/processed/adrq3/I/I_mix_terms_3q26.csv` (one row per term: term, value, unit, adr_contribution_pp, lo, hi, basis, source_file).
5. Write `research/notes/adrq3/I_adr-mix-terms-3q26.md` in the BRIEF format (bottom line, tables, method, what it can and cannot identify, next evidence, files).

## To finish workstream J (residual and card v2)
1. Wait for J1 to exit, then `py -3.13 analysis/src/adrq3/J1b_calendar_tests.py` (does listed-price y/y track ADR ex-FX and the residual over 2024Q3-2025Q3, same-quarter and one ahead).
2. Confirm `proxy_tests.csv` is complete; if J2 is still running, wait.
3. Re-run `py -3.13 analysis/src/adrq3/J3_residual_nowcast_card_v2.py` once `data/processed/adrq3/I/I_mix_terms_3q26.csv` exists, so card v2 uses the measured mix terms; it rewrites `adr_card_v2.csv`, `card_v2_backtest.csv`, `residual_nowcast.csv` and the J3 files. The pre-registered test: does v2 beat naive "ex-FX same as last disclosed quarter" on the expanding walk-forward 2024Q1-2026Q2 (RMSE ratio below 1.0)? Report pass or fail and which term causes a failure.
4. Write `research/notes/adrq3/J_adr-pricing-residual-and-card-v2.md` in the BRIEF format, with the calendar-price backtest as its own section.

## Then
- Commit per workstream (`git add analysis/src/adrq3/I* data/processed/adrq3/I research/notes/adrq3/I_*` excluding `cache/`, `logs/` and anything over 50 MB; same for J). Never push without Krish.
- Write `docs/adrq3/SYNTHESIS.md`: the 3Q26 and 4Q26 ADR numbers with bands from v2 next to the H card, whether v2 passed the test, which mix terms are measured and validated, what the calendar-price backtest says about requesting 2026 price data from Inside Airbnb, and the decision list for Krish.
- The memory note `adr-q3-nowcast-run.md` in the Claude memory directory points here.

## If the numbers are needed before the agents can finish
The H card on main (`data/processed/q3nowcast/H/adr_forecast_card.csv`) stands: 3Q26 reported ADR +3.2%, $176.8, band 174.0-179.1; 4Q26 +3.9%, $174.1. The partial J outputs already on disk are a first cut of v2 with the H mix inputs and should be read as such.
