# GE-EVENT independent review

15 September 2026. Reviewer: roadmap_auditor, author of GE-FORECAST and not author of GE-EVENT. Read-only review of the event implementation, `GE_PREREG_v1.md`, event tests and canonical `data/processed/forecast_methods/gbv_event_v1/events_v1/run_v2/` outputs. No event source, model or output file was edited.

**Verdict: PASS for the bounded descriptive event audit, with the interpretation limits below.** No blocking numerical defect was found. This does not validate a causal guide-to-price law or a tradable strategy.

## Exact reviewed objects

| Object | SHA256 |
|---|---|
| `analysis/src/forecast_methods/gbv_event_v1/events/run.py` |1668e65f6a3c9a4e3f0416035cf736524e4d3b0c0f5d0575e94304ba9e5e9024|
| `analysis/src/forecast_methods/gbv_event_v1/events/test_events.py` |f0414ad3817858bc64b51fb5b7691e9644e717b79d4106a19ee885f50357c202|
| `events_v1/run_v2/receipt.json` |da8d759611ccd4c20bea2d15abc7c0204a440405b2dd140cb68d9017b939eaa2|

The receipt binds all input hashes and12 output hashes. Every binding was independently verified against disk. Engineering check counts are not extra historical observations.

## What was checked

The focused command exited0 with7tests passing:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -m pytest analysis/src/forecast_methods/gbv_event_v1/events/test_events.py -q -p no:cacheprovider
```

A separate in-memory calculation, without calling the author's calculation functions, passed736 source/identity checks. It reconstructed all daily legs directly from the OHLC table, benchmark differences, all primary regression slopes via independent least-squares calculation and correlations, all source/output hashes, input chronology and the earlier-origin joins. It left no new model/output files. Results:

- All23 frozen ledger events are retained, with20 numeric forward guides. Eligibility gives16 original attributed revenue-consensus comparisons and15 cushion-adjusted comparisons. Event inclusion is not filtered on unusually large moves, sign or forecast success.
- The primary register selection fixes the original `PG-<guided quarter>-revenue` row and role; DoltHub remains a separate mirror sensitivity. Missing/quarantined original rows are not backfilled from the mirror. Same-day original consensus relies on the documented morning convention; the code does not establish exact intraday timestamp provenance independently.
- Guided-quarter joins match each earnings event's next-quarter target. Forecast-target W1/W2 and event-print W1/W2 are distinct and labeled. All21 candidate forecast rows, including abstentions/live unmatched rows, are preserved.
- Every cushion training actual publication precedes the event. The just-reported current quarter is excluded from that policy calibration. Missing policy history remains missing.
- For every security/event, the preclose is the actual event-date close and the entry is the next matched ABNB/QQQ session open. No duplicate security/date rows exist in the audited source. All gap, session, close-to-close and5/20session returns reproduce; all115 comparisons to frozen returns match.
- Excess means **ABNB simple return minus QQQ simple return**. Exact close-to-close compounding is performed per security before differencing, including the difference of cross terms. The maximum residual is4.31e-14percentage points. Compounding excess gap and excess session as if they were one security would be wrong; the code does not do so.
- Earlier-origin comparison uses a DoltHub snapshot strictly before the actual forecast origin. It does not substitute event-morning consensus. The audit also calculates origin-close to next-open/next-close returns, so an early position is not credited with only the isolated earnings gap while ignoring intervening exposure.
- Twelve primary statistical comparisons cover two signals, two price legs and all/W1/W2. All primary Holm-adjusted permutation p-values equal1.0. Primary slopes/correlations match independent recomputation. Current-print revenue-surprise controls use identical complete rows for the controlled/uncontrolled comparison; vendor, longer-return and pre-event associations remain secondary descriptions.

## Required interpretation in the workbook/memo

Both published-guide variables become known only after publication. Published guide divided by revenue consensus is a different-object diagnostic. Dividing Street revenue by an assumed pre-event cushion creates a hypothetical guide comparator, not observed guide expectations. Simultaneous current earnings/news prevent causal attribution from these correlations. Conditional controls, small-sample Fisher/HC1 intervals and permutation exchangeability assumptions do not fix identification or establish a trading rule.

The earlier-origin implied-guide signal has an additional useful identity: `candidate_guide / (origin_Street_revenue / shared_cushion_divisor) - 1` equals `candidate_revenue / origin_Street_revenue - 1`. The common cushion cancels exactly. This is a revenue disagreement expressed on a hypothetical common guide basis, not an independent source of guide-expectation evidence. The reviewer sent this presentation clarification to the event author and parent.

The package has not implemented a signed position-sizing/entry/exit/cost strategy. It correctly makes no net-after-cost or strategy-promotion claim. A failed/weak descriptive association is not itself a complete executable P&L backtest. Any future trading statement must explicitly specify information available at entry, the holding period, costs, sign-group counts and event/year robustness before promotion. No additional strategy model is required to complete this bounded descriptive audit.

Daily prices cannot identify during-call moves, release-versus-call legs, wick ordering or stop/target execution. Those remain unavailable and must not be visually reconstructed as observed intraday candles. Event-time source provenance remains the source auditor's separate contract.

## Minor documentation follow-up

The README's sample output path is the already-existing `events_v1` parent. The reviewer asked the author to identify canonical `events_v1/run_v2` and show a fresh output ID for replay. This affects ease of reproduction, not the reviewed numbers. No numerical rerun is necessary for either this path clarification or the common-cushion identity explanation.

## RESUME

Parent may consume the exact reviewed `run_v2` event tables and charts as descriptive historical evidence. Preserve full event eligibility, distinct expectation definitions, forecast-origin exposure and absent intraday coverage. No blocking arithmetic issue remains. If event code or numerical outputs change, bind and review the new version before carrying this PASS forward; documentation-only clarification does not alter the pinned numerical acceptance.
