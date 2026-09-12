# l1-reconciliation

Layer 1: constrained least-squares reconciliation of regional nights and regional
ADR to the interval-censored disclosures and the 72 exact filed regional revenue
cells, plus the FY27 named decomposition.

## Run command (exact)

```bash
cd "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB"
python analysis/src/forecast_methods/l1_reconciliation/run.py
```

Rebuilds everything under `data/processed/forecast_methods/l1_reconciliation/` and
registers three objects in `data/processed/forecast_methods/registry/`. Exit code 0
on success. Safe to re-run.

## NUMERAIRE HEADER (required by the addendum)

This package hands **reported ADR** — GBV in reported USD divided by
Nights-and-Seats — **not** host payout per night and **not** `usd_constant`. It
does **not** de-gross-up the fee migration. The single de-gross-up equation lives
in `fee-takerate` and only there.

## BOUNDARY RULE

Exactly **one** object crosses onward: **GBV in USD, booking-dated, one number per
quarter** (`l1_gbv_spine_quarterly.csv`). Nights, ADR, regional mix, unit size,
LOS, seats and regulation do **not** cross the boundary.

## Why the 72 exact cells are hard constraints and not penalties

Free parameters are only (i) K−1 = 3 softmax logits per quarter for the regional
share of Nights-and-Seats and (ii) 3 time-invariant regional take-rate tilts with
3 linear drifts (APAC is the reference). Everything else is *solved*:

```
s_{r,q}   = softmax(a_{.,q})                     regions sum to 1 EXACTLY
n_{r,q}   = s_{r,q} * N_q                        nights identity EXACT
tr_q      = [sum_r Rev_{r,q}/m_{r,q}] / GBV_q    closed form
GBV_{r,q} = Rev_{r,q} / (tr_q * m_{r,q})         72 filed cells EXACT by inversion
ADR_{r,q} = GBV_{r,q} / n_{r,q}                  OUTPUT
blended   = sum_r s_{r,q} * ADR_{r,q}            geographic mix is an OUTPUT
N_q       = n_home + n_hotel + s_exp + s_svc     seats/hotel dilution is an OUTPUT
```

So the −0.41pp calibration plug is retired by reparameterisation and the +0.19pp
current-weighting index bias is arithmetically impossible.

## Files

| file | contents |
|---|---|
| `l1_panel_quarterly.csv` | the reconciled panel: quarter × region nights, share, reported ADR, GBV, revenue, take rate |
| `l1_gbv_spine_quarterly.csv` | **the one object that crosses the boundary** |
| `l1_residuals_by_constraint.csv` | every constraint, its band, the fitted value and the hinge residual |
| `l1_residual_summary.csv` | residuals aggregated by constraint class, with n |
| `l1_feasibility_ladder.csv` | which disclosure classes can hold simultaneously (the G2 diagnostic). Carries `adr_constraint_weight` = 1.0: the ladder fits ADR at FULL weight, unlike the headline fit (`W_CONF adr = 0.25`), so the two worst-gap figures are different statistics |
| `l1_acceptance_tests.csv` | the numbered acceptance tests, pass/fail, with numbers |
| `l1_annual_adr_decomposition.csv` | (b) validation against `2026-09-07_adr-decomposition.md` |
| `l1_bootstrap_intervals.csv` | 4-quarter block-bootstrap p10/p50/p90 on shares, nights, ADR |
| `l1_denominator_identity.csv` | N = home + hotel + experiences + services and the closed-form home price |
| `l1_regional_fx_pp.csv` | regional FX pp on ADR, disclosed-pair where both integers exist, basket otherwise |
| `l1_kernel_lambda_local.csv` | seasonal λ recomputed locally at w = 2/3 |
| `l1_fy27_revenue_grid.csv` | FY27 under driver-base and data-only continuation × kernel w ∈ {0.33, 0.50, 0.667} |
| `l1_kernel_weight_sensitivity.csv` | FY27 spread across the kernel-w grid in $M, % of revenue and pp of growth (computed, not quoted) |
| `l1_fy27_growth_decomposition.csv` | the named, non-overlapping FY27 decomposition |
| `l1_run_log.txt` | the console log of the last run |

## Registered objects

* `l1-reconciliation__revenue_contemporaneous` — one-quarter-ahead revenue from the
  reconciliation at every W1 and W2 guide date, both replays.
* `l1-reconciliation__fy27_revenue` — 2026Q3…2027Q4 revenue, LIVE at 2026-09-11.
* `l1-reconciliation__fy27_growth` — the same on `revenue_yoy`.

## Not built (by instruction)

The joint hedonic; the 120-market panel; separate price and sub-mix states (exactly
collinear — the +2.9pp is reported as an unidentified 2-d ridge and is **not**
split); a separate party-size driver; the 1.67 regulation multiplier; any fix to
new-business netting; any state space (Stan or PyMC).
