# WP-C1 — Thesis C — calendar pickup ≤ 90 days as a booked-GBV feature

**Lane:** Theo lane · **Effort:** 3–5 days (needs consecutive monthly calendar dumps) · **Needs from outside the repo:** Inside Airbnb calendar dumps — public, download yourself (see 04_DATA_MAP.md); ~1–3 GB per month for 34 markets

You are a contributor to the Citadel-ABNB pitch (Airbnb, 2026 Citadel Intercollegiate Stock Pitch Competition; memo due
2 Oct 2026; finals 22–24 Oct; next print 5 Nov). This work package is part of the **kernel / top-down thesis**: Airbnb's
revenue is mostly *converted* from bookings that are already printed, the guide is that revenue over a shrinking cushion,
and the Street misreads the composition of growth as demand. Read `docs/thesis-kernel-topdown/README.md` and
`01_CONTEXT.md` first (10 minutes), then this file.

## The task
**Why.** 97% of next-print revenue uncertainty is booked GBV. The team's earlier alt-data tests targeted nights and revenue growth and
failed; the same data aimed at bookings has never been tried. Calendar *blocked* rates are U-shaped past ~90 days (owner blocks), so
only short-horizon flips are bookings (K2 finding).

**Build `pickup_v1/`:** for consecutive monthly Inside Airbnb calendar dumps of the same market (2024–25 vintages exist for 34 markets;
2026 vintages arrive monthly), for the same listing_id and stay date, count nights that flip available → unavailable between dump t−1
and dump t, restricted to stay dates ≤ 90 days ahead of dump t. Aggregate by market and month; weight by listing price where the dump
carries one (2024–May 2025 only), otherwise by nights; build a y/y pickup index (same market, same calendar month); calibrate
cross-sectionally to disclosed GBV y/y on the 13 quote cities; test PIT on W2 (W1 has no vintages). Use DuckDB over the gz files;
never load a calendar into pandas whole. Document the blocked-vs-booked caveat and the horizon cut.

## Pass line (pre-registered — write it in your note before running)
Right-signed correlation between the pickup y/y index and disclosed GBV y/y on the available quarters, AND the index beats the
RNPL-corrected unearned-fees baseline (K1) on W2 as a GBV nowcast. Publish the negative if it fails — that is still a result.

## Outputs
`pickup_v1/` with the DuckDB pipeline and manifests (SHA-256 of every dump used); registry `pickup-v1__gbv_yoy_current_q`;
note `05_backtests/ALPHA_C1_PICKUP.md` with the horizon-sensitivity table (30 / 60 / 90 / 180 days).

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
