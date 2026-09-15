# PR41 H and PR44 ADR audit

Reviewed GitHub PR44 head `573b3770e80ef4418bcc8c75a4cf0dcf906fc8f9`, including inherited PR41 H1. All evidence was fetched through the GitHub connector. No production code or GitHub comments were changed.

## Confirmed findings

### P2 — Refit H1's AR(1) benchmark before each forecast

Location: `analysis/src/q3nowcast/H1_adr_card.py:258-263` (PR41).

The comment promises an AR(1) fit before the backtest, but `ar_src = hh['adr_exfx_yoy_pp']` uses the entire 1Q23–2Q26 history, followed by one fit for all scored quarters. Thus the 2Q24 forecast includes 2Q24 and later outcomes in its fitted coefficients. Refit inside the quarter loop using observations strictly before the target quarter. On the identical nine quarters, committed AR(1) RMSE is 0.803598 pp; expanding pre-quarter RMSE is 1.058282 pp, 31.7% larger. The reported 0.80 pp benchmark is optimistic. The component model still loses to naive; this changes benchmark validity, not that conclusion. PR44's J3 implementation already refits AR(1) correctly but does not repair the original H file or published H result.

### P2 — Preserve downside asymmetry in the ADR scenario band

Location: `analysis/src/adrq3/J3_residual_nowcast_card_v2.py:187-193` (PR44).

The code centers `sqrt(sum(((high-low)/2)^2))` on each term's chosen point even when the point is far from its range midpoint. The principal residual input is low 2.3983 / point 4.6150 / high 4.8493 pp: 2.2167 pp downside but only 0.2344 pp upside. The symmetric calculation produces a reported Q3 range +1.70% to +4.35%, excluding the explicitly discussed mean-reversion case +0.81% ($172.68 ADR), even with every other assumption unchanged. That one-term scenario lowers Q3 GBV by about $557m. Separate downside/upside RSS distances would be 2.2579 / 0.6790 pp rather than 1.3278 / 1.3278; preferably publish a direct residual scenario table because these inputs are scenario bounds, not estimated standard deviations. The detailed note discloses the wider arithmetic interval and downside case, so this is a misleading headline-band construction, not a hidden scenario.

### P2 — Rebuild I3 and I5 in the documented September refresh

Location: `docs/adrq3/SYNTHESIS.md:42` (PR44); dependency evidence in `analysis/src/adrq3/I5_summary.py:82-104` and `analysis/src/adrq3/J3_residual_nowcast_card_v2.py:119-148`.

Following the documented steps (E, I1, I1b, then J3) leaves the current card unchanged. I1b updates party-size windows; E updates the regional reviews series. Neither writes `I_mix_terms_3q26.csv`, the only measured-term input J3 reads. I3 must first translate the fresh E split into `I3_geo_mix_3q26.csv`, and I5 must rebuild the summary consumed by J3. Add those stages to the refresh command, or provide one orchestrator with source-vintage/freshness checks so successful execution cannot silently republish the August card.

### P2 — Remove the causal claim that zero median price change rules out repricing

Location: `docs/adrq3/SYNTHESIS.md:29` (PR44).

The synthesis says hosts do not reprice existing dates and realized ADR growth comes from composition/new listings. Its own matched-panel results contradict the first clause and do not identify the second. For the May-2025 snapshots' 0–90-day matched panel, the median change is zero but the matched mean price changes +2.6177% in EMEA and -1.1867% in North America. Identical listing-date pairs have equal observation weights on both sides, so those mean differences require price changes within the matched panel. The separate fixed-stay-date revision diagnostic shows 6.74% of observation-weighted matched dates changing by more than 0.5% between snapshots (all-availability sample). A zero median establishes that a majority is unchanged, not that the contribution to average ADR is zero. Retain the valid conclusion that current price coverage is missing and this panel has not validated a residual forecast; remove the unsupported economic attribution and blanket dismissal of price research.

## Reproducibility issue to consolidate with the wider audit

Every PR44 pipeline uses `MAIN = C:\Users\krish\citadel-abnb`; H1 additionally uses a separate unmerged worktree path `C:\Users\krish\citadel-abnb-overnight2`. J3 reaches the first hardcoded processed-data dependency at line 112. That path is absent in the user's checkout. Resolve repository data relative to the script and allow an explicit raw-data root. PR44 also references raw `external_prices` JSON and a manifest in the narrative, but none is included in its 50 changed files; the pipeline has no acquisition function. Shared source access and an executable refresh need to be documented, not assumed.

## Checks and limits

- `reproduce_adr_findings.py` reconstructs the H1 AR(1) comparison from committed history and backtest CSVs and computes all quoted band/scenario and calendar statistics. Results are in `audit_evidence.json`.
- Point ADR, GBV and same-quarter-take-rate revenue arithmetic reconciles to the committed J3 outputs up to rounding.
- J3 correctly discloses its realized target-quarter mix backtest as an upper bound on what workstream I could measure; that alone is not a hidden-leakage finding.
- LOS blocking versus actual bookings, survivor listings, missing transaction prices, small samples and weak forecasting tests are substantially disclosed. No standalone finding is based merely on those limitations.
- The large raw calendars/reviews were not downloaded or reprocessed. Calendar-statistic evidence checks committed aggregates and the code that constructs them, not the integrity of the underlying raw vendor snapshots.
- LOS fixed-calendar windows are not simultaneously lead-matched (0 of 65 vintage pairs is exactly 364 days apart; maximum gap mismatch 45 days). The code deliberately provides separate lead-matched and calendar-window sensitivities, so this is a wording caution rather than an additional finding.
