# q3nowcast_v2 / E: the Mar-May 2023 Inside Airbnb reviews vintage (WP-K build A)

Copies of the workstream E scripts (`analysis/src/q3nowcast/E3_review_counts.py`, `E4_build_index.py`) pointed at
a NEW output folder `data/processed/q3nowcast_v2/E/`, with the 116-market Mar-May 2023 reviews mirror
(Hugging Face `alujjdnd/Airbnb-Mar-2022-2023`, `raw_dl/`; data Inside Airbnb, CC BY 4.0) added as a second
vintage beside the held Aug/Sep 2025 and Jun-Aug 2026 dumps. Nothing under `analysis/src/q3nowcast/` or
`data/processed/q3nowcast/` is touched; the raw files live outside the repo in
`C:/Users/krish/abnb_ia_capture/ia_reviews_vintage2023/` (never in `MAIN/data/raw/inside_airbnb_reviews`).

Command (from the worktree root):

    py -3.13 analysis/src/q3nowcast_v2/E/run.py                 # full rebuild incl. the 4.88 GB download (resumable)
    py -3.13 analysis/src/q3nowcast_v2/E/run.py --skip-download # re-verify the raw store, then recount / retest

Outputs: `data/processed/q3nowcast_v2/E/` (raw manifest with sha256, market_vintage_monthly.csv with the 2023
vintages, E4 tables, T1 and T2 test tables) and `data/processed/regulatory_v2/` (NYC LL18 bracket and T3).
Note: `docs/revenue-forecast-strategy/05_backtests/WPK_reviews-index-2023-vintage.md`.

Interpreter: the repo venv `python` (3.11) has no pyarrow on this machine; use `py -3.13` (pandas 2.3.3, pyarrow 24), as the v1 E scripts do. `run.py` passes its own interpreter to every step.
