# Joint cohort early-origin forecasts — harness comparison limitation

15 September 2026. Identified by parent before new registrations. No frozen harness changes requested within this task; this note records a future change request and the current workaround.

## Finding

The frozen `harness/score.py` builds its naive baseline map using `(target, window, prior_basis, quarter)` and omits `vintage_date` and `horizon_q`. It then looks up that map for every candidate. It does not substitute a candidate's optional `base_naive` value. FORMAT 1.1 preserves the same scoring code.

The new joint-cohort replay predicts a target quarter's guide at the previous earnings release, before the release issuing that guide. Existing registered revenue baselines can have a later information date for the same target quarter. A scoreboard ratio can therefore compare different information sets. The absolute RMSE/MAE/bias still describes the registered prediction errors, but the automatically derived naive ratio, `beats_naive` and `survives_both_windows` cannot establish the new candidate's same-origin forecast superiority.

## Workaround for this package

Register genuine historical candidate rows under new method/object names with exact early origins, preserving failed candidates. Run both unchanged scorers into new output directories and verify existing rows/files remain unchanged. Use the quant package's paired, same-origin fixed-kernel comparison and preregistered tests for the pitch-use decision. Do not quote a frozen-scoreboard promotion flag for this early-origin object. No late-origin baseline is relabelled early-origin.

## Requested future version

Match baseline and candidate on information date/horizon in addition to target, quarter and replay/window, or explicitly accept a validated same-origin baseline carried with the candidate. Reject or flag unmatched comparisons. Implement only in a new version with historical preservation tests; do not overwrite the frozen harness.

## RESUME

Parent must bind the actual new registry rows and scoring receipts after review. Preserve this limitation in the final technical note. A same-origin forecast comparison from the quant package is the relevant decision statistic regardless of any generic scoreboard ratio or promotion label.
