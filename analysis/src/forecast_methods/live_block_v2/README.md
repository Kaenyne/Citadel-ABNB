# live-block-v2 — one reconciled 3Q26 printed take rate

Task B1. Fixes RED_TEAM.md **F3**: three mutually inconsistent live 3Q26 take rates
(17.81 % / 18.14 % implied / 18.40 %) and a 0.22 pp break in `GBV = nights × ADR`.

**COPY, NEVER OVERWRITE.** This package reads `optimal_mix/`, `fee_takerate/`,
`kernel_lambda/` and the registry. It writes only into
`data/processed/forecast_methods/live_block_v2/` and the five new registry files
`registry/live-block-v2__{revenue,gbv,nights,adr,take_rate}.csv`. It does not run
`harness/score.py`.

```bash
cd "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB"
python analysis/src/forecast_methods/live_block_v2/run.py
```

## Files

| file | what |
|---|---|
| `combine.py` | verbatim copy of `optimal_mix/combine.py` (schemes + `mixture_moments`), kept so this package never imports the original |
| `reconcile.py` | new: the kernel reproduced from `kernel_lambda/kernel.py`, the walk-forward error correlation, and the joint draw |
| `run.py` | the run |

## Method in one paragraph

The two identities imposed are ABNB's own definitions, not modelling choices:
ADR is *defined* as GBV ÷ Nights and Seats Booked, so ADR is the residual; and the
printed take rate is revenue ÷ **same-quarter** GBV. Revenue, GBV and nights are
carried unchanged from the optimal-mix live combination (their published marginals are
already Gaussian on the level — `q10 = point − 1.2816·sd`), drawn jointly with the
correlation of their **combined walk-forward percent errors** taken from
`optimal_mix/05_combined_walkforward.csv` at the same pool and scheme each live object
was built from. ADR and the take rate are then computed inside every draw, so the
identity holds to machine precision and the take-rate distribution is derived **once**.

## Harness change request

`take_rate_pct` and `adr_usd` have no registered naive / AR(1) / trailing-4 baseline, so
`rmse_ratio_to_naive` is NaN and `survives_both_windows` is a vacuous `False` for these
two objects (RED_TEAM §6.3 and harness change request 1 already say this). Until
baselines exist for them, the `live-block-v2` take-rate and ADR rows must be read as
**identity outputs of scored objects**, not as separately scored forecasts.
