# WP-C3 — Retarget the alt-data features at booked GBV and at the kernel residual

**Lane:** Krish lane · **Effort:** 2–3 days (after WP-C1 or on the ledger features alone) · **Needs from outside the repo:** nothing beyond the repo for the ledger features; WP-C1 outputs for pickup

You are a contributor to the Citadel-ABNB pitch (Airbnb, 2026 Citadel Intercollegiate Stock Pitch Competition; memo due
2 Oct 2026; finals 22–24 Oct; next print 5 Nov). This work package is part of the **kernel / top-down thesis**: Airbnb's
revenue is mostly *converted* from bookings that are already printed, the guide is that revenue over a shrinking cushion,
and the Street misreads the composition of growth as demand. Read `docs/thesis-kernel-topdown/README.md` and
`01_CONTEXT.md` first (10 minutes), then this file.

## The task
Re-point the 598-feature walk-forward machinery (`analysis/src/overnight/08_altdata_backtests.py`, `08_feature_tests_all.csv`) at two
new targets: (a) booking-dated GBV y/y for the quarter in progress, and (b) the kernel residual R_q = revenue_q − carried part from
`data/processed/forecast_methods/kernel_phi_v2/`. Pre-register the feature list in your note BEFORE running (include: RNPL-corrected
unearned fees growth, funds-payable growth, GBV momentum, NTTO arrivals, the reviews stays index (Krish's E), calendar pickup if WP-C1
exists, hotel RevPAR; exclude Google Trends and macro sentiment — they failed and are not PIT). PIT, both windows, nested expanding-window
CV for anything with tuned parameters.

## Pass line (pre-registered — write it in your note before running)
A feature earns a place only if it beats the ledger baseline (RNPL-corrected unearned fees) on GBV on BOTH windows with a stable coefficient
sign. Report everything that did not, with ratios.

## Outputs
`gbv_features_v1/`; registry rows for any survivor; note `05_backtests/ALPHA_C3_GBV_FEATURES.md`.

## Standing rules (same for every contributor — do not skip)

- **Repo:** clone `https://github.com/Kaenyne/Citadel-ABNB`, branch from `main`, read `CLAUDE.md` / `AGENTS.md`, then
  `docs/revenue-forecast-strategy/AGENT_BRIEF.md` and claim this WP in `docs/revenue-forecast-strategy/WORKBOARD.md`.
- **Copy, never overwrite.** New folder `analysis/src/forecast_methods/<pkg>/` (with `run.py` exiting 0 and a README),
  outputs in `data/processed/forecast_methods/<pkg>/`, registry files only under a NEW method name, your note as a NEW file
  `docs/revenue-forecast-strategy/05_backtests/<WP>_<slug>.md`. Never edit `harness/`, `L0/` (append-only, backup first),
  another package, or any tracked data file.
- **Point-in-time.** Refit at guide dates; consensus only from `data/processed/forecast_methods/L0/L0_vintage_register.csv`
  with vendor + timestamp before the date; windows W1 (1Q23+, n≈14) and W2 (1Q24+, n≈10); a result must survive both;
  letter-rounded integers scored on [x−0.5, x+0.5].
- **Pre-register the pass line** (given below) before running; publish a failure as a result.
- **Harness format 1.0** is authoritative: `analysis/src/forecast_methods/harness/README.md`. Register with `register()`,
  then run `python analysis/src/forecast_methods/harness/score.py`.
- **Baselines every object must beat:** naive / AR(1), trailing-4, guide × (1 + trailing-8 cushion), the vintage-stamped Street;
  for GBV also the RNPL-corrected unearned-fees series (K1).
- **Never quote the kill list** (`AGENT_BRIEF.md` §6). Never commit licensed data (Bloomberg, Third Bridge, LSEG exports) or raw stores.
- **Git:** your branch `<name>/<wp>`; PR to `main`; one teammate reviews. Nothing to `main` directly.
- **Python:** `python -m venv .venv && pip install -r requirements.txt pymc arviz scikit-learn pyarrow linearmodels lightgbm duckdb`.
  Run from the repo root; resolve paths with `pathlib`.

## How to finish

Write the note with the template in `AGENT_BRIEF.md` §7 (verdict first; exact commands; tables with n; PIT vs full-sample labelled;
vendor + timestamp on every consensus number; what failed; a `RESUME` paragraph). Update `WORKBOARD.md`. Open the PR.
