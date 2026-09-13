# Regional kernel v1

Run from the repository root with its `.venv` interpreter:

```
python analysis/src/forecast_methods/regional_kernel_v1/run.py
python -m pytest analysis/src/forecast_methods/regional_kernel_v1/tests -q
```

This is an identification audit and conditional regional FX reconstruction. Annual revenue / GBV is measured; quarterly regional GBV is modelled. The reconstruction date is 2026-09-12. Historical reconstructed values are not historical forecasts. The O-D matrix mixes dated public tourism proxies with explicit assumptions and cannot replace a measured Airbnb currency-exposure matrix.

`engine.py` contains the independently callable accounting, exposure validation, point-in-time refusal, fixed-lag translation and interval-likelihood functions. `run.py` rebuilds only this package's files. Public numeric extracts and provenance are in `public_inputs.csv`; no raw stores or licensed exports are included. Network is not needed to rebuild.

K0 handoff uses USD booking-dated GBV, coefficients in percent and explicit publication dates. Run the regional K0 call at 2026-09-13, strictly after this reconstruction's timestamp. The live analytical snapshot itself is labelled 2026-09-12; no historical registry date is invented to bypass the frozen harness's 2026-09-11 date constant.

The scenario guest-fee share grid is 0, 0.5 and 14.1/(14.1+3)=0.82456 of fee revenue. These are endpoint/midpoint sensitivities, not estimates of migration penetration. Origin-region and currency are distinct. International travel within EMEA remains on the O-D diagonal and does not imply a cross-currency booking. The 46% cross-border disclosure is an old gross-nights observation, carried only as a labelled scenario. The ADR pass-through estimates retain their published short-sample limits and do not establish fee-currency exposure.
