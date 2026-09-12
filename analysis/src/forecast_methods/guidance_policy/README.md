# guidance-policy

The guidance policy function: the cushion, the range width, the at-print consensus
(kappa), the point-in-time backtest of the GUIDE forecast, the live 4Q26 guide
distribution, the nights bucket words, and the 9/9 guide-below-Street rule.

## Run command (exactly this, from the repo root)

```bash
cd "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB"
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/guidance_policy/run.py
```

Exit code 0 on success. Rebuilds every CSV under
`data/processed/forecast_methods/guidance_policy/` and re-registers five objects.
Writes progressively: each section writes its outputs before the next runs.

Then re-score:

```bash
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/harness/score.py
```

## Files

* `run.py` — entry point, sections A..I, one per spec item.
* `lib.py` — the policy primitives: cushion, block bootstrap, local recognition kernel.

## Registered objects (harness format v1.0)

| object | target | windows | n_params |
|---|---|---|---|
| `guide_mid_next_q` | `guide_mid` | W1, W2 x {PIT, full_sample} | 6 |
| `print_from_guide` | `revenue_musd` | W1, W2 x {PIT, full_sample} | 1 |
| `print_kernel_policy` | `revenue_musd` | W1, W2 x {PIT, full_sample} | 5 |
| `q4_2026_guide_mid` | `guide_mid` | LIVE (2026Q4, 15-row GBV x fee grid) | 6 |
| `q4_2026_print` | `revenue_musd` | LIVE (2026Q4, same grid) | 6 |

`n_params` counts only what enters the registered `point`/`q50` (and, for
`q4_2026_print`, its predictive sd): 4 seasonal lambda + 1 lag weight w + 1 cushion c.
kappa is fitted and published but is NOT in any of these points — it feeds only the
informational at-print-consensus column — so the count is 6, not 7. Corrected after
verification round 1.

The two LIVE objects are written with `register(..., strict_windows=False)` because the
harness's `window_of_target("2026Q4")` returns `[]` (2026Q4 is not a guide event yet).
See the harness change request in the note.

## The policy function

```
guide_mid_q   = E[Revenue_q] / (1 + c)      c = trailing-8 MEAN of actual/guide_mid - 1
print_q       = guide_mid_q * (1 + c)
cons_at_print = guide_mid_q * (1 + kappa)   kappa = at-print Street over guide mid
E[Revenue_q]  = lambda_season(q) * [2/3 * GBV_{q-1} + 1/3 * GBV_{q-2}]
```

Cushion is `actual / guide_midpoint - 1`: directly observed and kernel-free. It is
never `guide / model`, which absorbs kernel bias one-for-one.
