# Analysis

- `notebooks/` - exploratory Jupyter notebooks (clear outputs before committing)
- `src/` - reusable Python: data loaders, chart helpers
- `figures/` - exported charts that go into the deck. Name them `NN_short-description.png` in deck order.

## Listing churn execution

Start with the [broad panel results](../research/notes/2026-09-07_listing-churn-broad-panel.md).
`acquire_churn_panel.py` and `measure_churn_panel.py` execute the full team historical
inventory. `acquire_churn_archive.py` and `measure_churn_archive.py` extend it to the
public September/December/March/June archive with explicit geography and coverage
screens. `report_listing_churn.py` produces the research memo and a matplotlib figure.
The captured public archive index is retained in `data/manifests/` for reproducibility.
All granular listing and candidate-unit records stay under ignored raw storage.

The [platform-history follow-up](../research/notes/2026-09-07_listing-platform-history.md)
tests property identity and other-channel advertising before and after disappearance.
`screen_platform_mentions.py` screens existing descriptions; `probe_listing_archives.py`
and `index_listing_archives.py` collect public archive metadata;
`summarize_platform_history.py` verifies the reviewed ledger and joins actual Airbnb
dates. Historical advertising, publisher-claimed dates and unknown operation remain distinct.

The [fee and churn time-series study](../research/notes/2026-09-07_fee-churn-catalyst.md)
adds earlier quarters and monthly fee-event observations. `acquire_fee_churn_history.py`,
`measure_fee_churn_history.py`, `summarize_fee_churn.py` and `report_fee_churn.py` build
rolling disappearance rates, comparable confirmation cohorts, fee arithmetic and
explicit materiality scenarios. Exact treatment/PMS status is unobserved; no causal
fee effect or migration rate is estimated.

## Hotel funnel audit

The [hotel operating audit](../research/notes/2026-09-07_hotel-funnel-audit.md)
contains global room sizing, a defined 25-market evidence table (24 comparable
listing pairs), supply and credit sensitivities, and the separate historical
13-market sensitivity. `audit_hotel_funnel.py --panel archive25` reads existing
captures; `model_hotel_funnel.py` computes explicit scenarios and the joined market
table; `verify_hotel_capacity.py` reconciles official spreadsheets;
`report_hotel_funnel.py` builds the memo/figure. `audit_hotel_overlap.py` records
visible GitHub/local evidence; `--sources-only` compares the current source ledger
against that frozen review. Overlapping captures are never pooled across panels.

See [measured results and exact replay commands](../research/notes/2026-09-07_listing-churn-execution.md).
`fetch_listing_churn_inputs.py` reacquires team-catalogued raw snapshots;
`execute_listing_churn.py` measures persistent absence and supported license-linked
continuation; `summarize_listing_destinations.py` reconciles the fixed manual evidence
ledger with its random sample. These scripts use only the Python standard library.

`extend_fee_churn_recent.py` adds June–August intervals for the same 13 team markets
and winter source-composition/reappearance diagnostics. `report_fee_churn_recent.py`
builds the [recent fee follow-up](../research/notes/2026-09-07_fee-churn-recent-followup.md).
Latest disappearance has unequal observation windows and no mature 90-day confirmation.

## Churn and hotel code review

Start with the [code and model-use audit](reviews/2026-09-07_churn-hotel-code-audit.md)
and its [per-file register](reviews/2026-09-07_churn-hotel-code-register.csv).
The selected hotel supply scope is now the [original 13-market panel](../research/notes/2026-09-07_hotel-original-13-market-coverage.md).
These studies support diagnostics and sensitivities; no direct forecast coefficient
or additive hotel revenue overlay is validated. The review explains how to use them
alongside the existing guidance, revenue, regulatory and fee-elasticity work.

Use Python 3.11+ and the repository requirements. Dated report builders verify frozen
input hashes before writing. Exact source replay requires the preserved, ignored raw
capture/extraction bundles; a fresh clone alone is insufficient. Run new observations
in a separate output directory or worktree so the reviewed studies remain reproducible.
