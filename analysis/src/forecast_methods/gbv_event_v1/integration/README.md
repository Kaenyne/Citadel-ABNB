# Four-quarter GBV conversion

From the review checkout root:

```powershell
python -B analysis/src/forecast_methods/gbv_event_v1/integration/run.py --out data/processed/forecast_methods/gbv_event_v1/integration_v1
python -B -m unittest discover -s analysis/src/forecast_methods/gbv_event_v1/integration -p test_integration.py
```

Existing output directories are refused. Reuses the operational fixed-weight K0 seasonal estimator at the frozen September 13 parameter cutoff and labels September 15 execution separately. The working GBV assumptions are imported from the existing L4 reference, including its explicitly inherited Q1 2027 input; this is not a promoted direct-GBV predictor. No nights/ADR/cost or annual model is built. Q2 revenue and implied guide now use Q1/Q4 GBV explicitly. Precise Q1/Q2 filing inputs are a separate sensitivity, not a silent recalibration. All expectation vendors stay separate; the selected comparison is Yahoo/LSEG with no cross-vendor fallback. Direct guide expectations remain unavailable.
