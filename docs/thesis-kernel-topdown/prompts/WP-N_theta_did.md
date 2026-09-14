# WP-N — θ by difference-in-differences from the fee-deadline price panels

**Lane:** Jessie lane · **Effort:** 2 days after the 18 Sep run · **Needs from outside the repo:** the capture CSVs under `data/processed/forecast_methods/fee_panels/runs/` (produced on Theo's machine; pushed after each run)

You are a contributor to the Citadel-ABNB pitch (Airbnb, 2026 Citadel Intercollegiate Stock Pitch Competition; memo due
2 Oct 2026; finals 22–24 Oct; next print 5 Nov). This work package is part of the **kernel / top-down thesis**: Airbnb's
revenue is mostly *converted* from bookings that are already printed, the guide is that revenue over a shrinking cushion,
and the Street misreads the composition of growth as demand. Read `docs/thesis-kernel-topdown/README.md` and
`01_CONTEXT.md` first (10 minutes), then this file.

## The task
**Context.** The single host-only 15.5% fee becomes the pricing deadline for hosts living outside the EEA on 15 Sep 2026 and inside the EEA /
Switzerland on 13 Oct (Resource Center article 771; note: keyed to host residence, no year printed — see `05_backtests/A3_fee_panels.md`).
Pass-through θ (how much of the fee hosts add to the listed price) is UNIDENTIFIED today and carries the whole fee edge (+1.1% of revenue at
θ 0.83 vs +4.05% at θ = 1). The capture returns LISTED prices only (fees and taxes do not render).

**Do:** on the 14 / 16 / 18 Sep runs (sample_ids.csv: 2,600 listings, 2,000 non-EEA / 600 EEA, fixed stays 13 Nov and 11 Dec): (1) measure
run-to-run panel overlap (same listing priced in consecutive runs) — if under 40% the design degrades to a city-level index, say so; (2) estimate
θ by DiD: change in log listed price for the migrating cohort (non-EEA cities) vs the EEA control across the 15 Sep deadline, with market and
stay-date fixed effects, clustered by listing; θ = jump ÷ 13.8pp (the gross-up needed for full pass-through); (3) report θ with a CI, the
implied revenue uplift range, and what the 12 / 14 / 16 Oct runs must show for the EEA cohort to confirm.

## Pass line (pre-registered — write it in your note before running)
Overlap ≥ 40% AND a θ confidence interval narrower than the current 0.83–1.41 window. If overlap fails, report the city-level estimate and label
it as such.

## Outputs
`fee_panels_theta/`; note `05_backtests/N_THETA_DID.md`; proposed replacement of the fee-uplift row in the card.

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
