# WP-E1 — Thesis E — does the kernel transfer? NCLH advance ticket sales

**Lane:** Jessie lane · **Effort:** 3–5 days · **Needs from outside the repo:** Alpha Vantage API key (free) or any source of NCLH quarterly financials; SEC filings

You are a contributor to the Citadel-ABNB pitch (Airbnb, 2026 Citadel Intercollegiate Stock Pitch Competition; memo due
2 Oct 2026; finals 22–24 Oct; next print 5 Nov). This work package is part of the **kernel / top-down thesis**: Airbnb's
revenue is mostly *converted* from bookings that are already printed, the guide is that revenue over a shrinking cushion,
and the Street misreads the composition of growth as demand. Read `docs/thesis-kernel-topdown/README.md` and
`01_CONTEXT.md` first (10 minutes), then this file.

## The task
**Why.** If a cruise line's revenue converts from its advance-ticket-sales balance with a λ as stable as Airbnb's, the kernel is a method,
not an Airbnb coincidence — and NCLH is on the competition's ticker list.

**Build `alpha_e_nclh/`:** pull NCLH 2015–2Q26 quarterly: advance ticket sales (balance sheet), passenger ticket revenue and onboard
revenue (income statement), capacity days, occupancy, net yield (press releases / 10-Q). Build revenue_q = c_s Σ_k φ_k ATS_{q−k} with
φ on the simplex over k = 0..3; estimate λ_s by season ex-COVID (drop 2020–21; flag 2022); within-season range; PIT walk-forward from
1Q23 vs naive, AR(1) and guide × (1 + cushion) using NCLH's own guidance history; if any consensus history is obtainable (Alpha Vantage
EARNINGS_ESTIMATES, press quotes flagged), run the WP-A guide-surprise test. Compare with ABNB in one figure (λ by season, both names).

## Pass line (pre-registered — write it in your note before running)
λ within-season range < 0.5pp over 2023–25 AND walk-forward ratio to naive < 0.6 on both windows; guide-surprise hit-rate ≥ 65% if
consensus exists. Publish the negative if it fails.

## Outputs
`alpha_e_nclh/` (data pull with manifest, model, figure); note `05_backtests/ALPHA_E_NCLH.md` with a one-page "does the method transfer?"
verdict first.

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
