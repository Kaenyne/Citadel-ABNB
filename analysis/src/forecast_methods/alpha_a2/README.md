# A2: guide-close surprise signal

From repository root, using the repository `.venv`:

```text
python -m pytest analysis/src/forecast_methods/alpha_a2/tests -q
python analysis/src/forecast_methods/alpha_a2/run.py
```

`--no-register` builds and validates the preview without writing the new method registry. The default rebuild registers only `alpha-a2__guide_mid_next_q.csv`; parent owns both scorers. No shared inputs are modified. Outputs: `data/processed/forecast_methods/alpha_a2/`.

Use `--no-register --output-dir <new-directory>` to validate in an isolated output snapshot while preserving the existing outputs and registry.

The K0 v2 module owns all kernel estimation and forecast quantiles. A2 calls with the calendar day after the letter to implement the harness's letter-close information set, then registers at the letter date. Historical pre-guide consensus must be stamped on/before that date, usable, attributed, and have pre-guide role. Explicitly quarantined rows remain unavailable. Return legs come exclusively from `returns_v1` next-open excess returns.

Date-only historical stamps retain CONVENTION's morning-of-print meaning and can be admitted on the letter date. Explicit intraday stamps must include a timezone and strictly precede 16:00 America/New_York on that letter date; exact-close, post-close and timezone-naive intraday stamps are rejected. UTC offsets and New York daylight-saving time are handled as instants, rather than by stripping the time or comparing calendar dates.

Main replay: nested PIT K0 selection and coefficients. The `ex_covid` column is a PIT sensitivity. `full_sample` fixes K0's full-history selected variant, refits coefficients and cushion at each date, and is a retrospective specification diagnostic. The guide-level registry does not consume Street; a guide-level row can exist with an unavailable consensus gap. Current consensus is used only in the live scenario CSV, deduplicated to three vendor families.

Live consensus stamps accept mixed date-only and full UTC timestamps. Selection orders normalized UTC instants, excludes future captures using the actual UTC run-start cutoff, and then keeps the newest observation in each vendor family. Same-day captures already available at run start are included. Date-only stamps are ordered at the start of their stated UTC date. The live table and audit record the exact cutoff; registry guide dollars do not depend on the selected consensus denominator.

Pass line and statistical choices were written in `docs/revenue-forecast-strategy/05_backtests/ALPHA_A2_GUIDE_SURPRISE_V2.md` before execution. Sample counts, availability reasons, inputs, timestamps, source IDs, controls, independent baselines, expanding ridge predictions and reproducibility hashes are explicit outputs. Small-sample bootstrap intervals are descriptive. W2 overlaps W1.
