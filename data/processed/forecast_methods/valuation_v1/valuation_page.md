# V — arithmetic reconciliation, 12 September 2026

**PARTIAL.** Arithmetic reproduces; inherited vintages and the translation of a change coefficient into an exit level remain unverified. No direction recommendation.

| Scenario / rank (n=1 each) | FY27 growth sensitivity | FY27 EV/EBITDA lens | Six-lens football field: mean [range], n=6 | Memo event analogue [implied multiple on fixed base EBITDA] |
|---|---:|---:|---:|---:|
| Bear | 9.18% → 15.47x → $170.64 | 13.5x → $108.46 | $74.18 [$37.23–108.46] | $140–152 (12.37–13.58x) |
| Base | 10.35% → 16.03x → $176.27 | 16.5x → $180.88 | $156.79 [$110.58–196.92] | $170–185 (15.40–16.92x) |
| Bull | 11.52% → 16.60x → $181.89 | 18.5x → $234.16 | $228.18 [$176.49–281.01] | $205–215 (18.94–19.95x) |

**Shown calculation:** multiple = 16.5 + 0.486022 × (growth% − 11.3086); price = (multiple × $5,685.7698M + $10,115.9869M) / 574.5982M. This holds EBITDA, cash and shares fixed; row ranks align for comparison and are **not the same scenarios**.

**Relation:** +0.4860 turns/pp, HAC 95% CI [0.3172, 0.6548], n=35 overlapping monthly changes, 4 parameters. This is Δ12 EV/**LTM** EBITDA against Δ12 forward-growth proxy, controlling for rates and Nasdaq valuation; it supplies a sensitivity, not an exit-multiple intercept. W1/W2 are diagnostics, with zero eligible independently vintage-verified scored forecasts. Source: regression_reproduction.csv; dates: monthly_vintage_audit.csv.

**Positioning:** $170.19, observed 2026-09-11 (Yahoo Finance via yfinance); refresh status price_refreshed. Short float 3.44% / 14,228,547 shares / 2.56 days (Yahoo settlement date 2026-08-31); targets mean $182.125, median $185, range $125–220 (n=40). Retrieval stamp 2026-09-13T00:18:59.397636+00:00; latest snapshot, not backdated to a guide date. Existing rating split pulled 6 Sep: 21 Buy / 11 Hold / 2 Sell (n=34); old target dispersion SD/mean 0.131 (n=31). The current range is a measure of dispersion; current target standard deviation is unavailable. These vendor panels have different membership.

**Three unresolved inconsistencies:** (1) Δmultiple/LTM and FY27 exit-multiple levels are different objects; a slope does not identify the intercept. (2) The preliminary exit recommendation uses older EBITDA/cash/shares: base $191.317 versus the final model's $180.88; the six-lens mean is a third object. (3) Memo branches are event analogues with unspecified earnings/cash/share bridges and a different horizon; +1 turn at fixed base inputs adds only $9.90, not the full bull-branch increase. All model prices retain the existing ~30 Sep 2027 target convention and weighted-average-share proxy caveat.

Evidence: growth_multiple_price_bridge.csv; football_field_reconciliation.csv; memo_branches.csv; input_manifest.json. No new valuation target has been adopted.
