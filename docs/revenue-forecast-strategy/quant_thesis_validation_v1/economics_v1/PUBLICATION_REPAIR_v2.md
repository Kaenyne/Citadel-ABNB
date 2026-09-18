# Economic publication label repair v2

2026-09-14 · parent review requested an additive correction to the ambiguous `actual_endpoint_balance_value` header. It might be read as measured future balances even though the protocol and surrounding table said the cash/share roll was conditional. That label is now `conditional_endpoint_balance_value` in canonical `results_v2/horizon_convention.csv`.

Every result table now carries `empirical_validation_n=0` and an explicit evidence-status field. Horizon tables state `conditional_cash_share_roll; FY27 EBITDA held constant; no current-price adoption`. The $182.867016 calculation is a **horizon-convention sensitivity**, not a newly underwritten twelve-month target or measured future value. Model source values and every numeric cell are unchanged; initial `results_v1` is retained.

Publisher source `publish_v2.py` checks all prior numerical-output hashes before copying, verifies the original cell strings are retained, and writes new receipts in a new directory. No numerical model or economic assumption is reopened. `README_FINAL_v2.md` gives both end-to-end commands and points to canonical outputs. `RESULTS_v1.md` retains its numerical conclusions, with this publication-status note governing canonical paths and labels.

## RESUME
Reviewer A uses canonical `results_v2`, independently reruns the underlying calculation and publisher into fresh directories, and checks the horizon-convention and economic wording. Parent should bind the reviewer receipt and canonical hashes before final handoff.
