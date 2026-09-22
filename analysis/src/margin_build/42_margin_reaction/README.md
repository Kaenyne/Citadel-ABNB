# 42_margin_reaction

Does margin news move ABNB? Post-print returns (vs QQQ) against the forward NTM consensus revisions each print caused, split into
revenue and margin, plus the stock arithmetic of a FY27 margin reset. Re-verifies the return file against Yahoo closes when
yfinance is reachable.

Run from the repo root (exit 0):

    py -3.13 analysis/src/margin_build/42_margin_reaction/run.py

Outputs: `data/processed/margin_build/42_margin_reaction/`. Notes: `docs/margin-build/notes/42_margin_reaction.md` and
`42_event_reasons.md`. Pre-registration: `docs/margin-build/notes/41_42_prereg.md`.
