# WP-A — Thesis A — the kernel predicts the guide better than the Street

**Lane:** Krish lane · **Effort:** 1 day · **Needs from outside the repo:** nothing — all data is in the repo

You are a contributor to the Citadel-ABNB pitch (Airbnb, 2026 Citadel Intercollegiate Stock Pitch Competition; memo due
2 Oct 2026; finals 22–24 Oct; next print 5 Nov). This work package is part of the **kernel / top-down thesis**: Airbnb's
revenue is mostly *converted* from bookings that are already printed, the guide is that revenue over a shrinking cushion,
and the Street misreads the composition of growth as demand. Read `docs/thesis-kernel-topdown/README.md` and
`01_CONTEXT.md` first (10 minutes), then this file.

## The task
**Claim.** At each print the kernel-implied guide (λ_season × [⅔ GBV just printed + ⅓ GBV one quarter earlier] ÷ (1 + trailing-8 cushion))
forecasts the actual guide with ~1.1pp error; the Street's expectation misses by ~2.5pp. When they disagree by more than 1pp the
sign of the guide surprise should be forecastable.

**Build `analysis/src/forecast_methods/alpha_a/`:**
1. For each guide date d on W1 (14 dates; extend to 19–23 with older consensus if a vendor-stamped value exists — flag those),
   compute the point-in-time kernel guide: c_s estimated on data through the previous quarter (reproduce the λ table in
   `05_backtests/kernel-lambda.md` first as your acceptance test), GBV of the quarter just printed on day d and of the quarter
   before, cushion = trailing-8 actual/guide-midpoint through d−1 (`data/processed/overnight/02_guidance_cushion_series.csv`).
2. Consensus for the guided quarter: latest vintage strictly before d from `L0_vintage_register.csv` /
   `data/processed/overnight/16_consensus_at_print_merged.csv`, vendor column kept. Never a September-2026 value for a historical date.
3. Signal S = kernel_guide − consensus (in % of consensus). Targets: (i) actual_guide_mid − consensus (sign and size; guides in
   `02_guidance_ledger.csv`); (ii) executable next-open returns at 1, 5, 20 days from `data/processed/abnb_earnings_reactions.csv`,
   `open_*` columns only, conditional on sign(S) and on |S| > 1pp.
4. Baselines: zero (always "in line"); sign of the previous guide surprise; the same rule with consensus as the base instead of GBV.
5. Report per-date table, hit-rates, conditional return means with n, both windows, and the live 5 Nov row (S for the Q4-26 guide
   against LSEG-family ~$3,159M, S&P $3,160M, Zacks $3,200M — three rows).

## Pass line (pre-registered — write it in your note before running)
Sign hit-rate ≥ 70% on |S| > 1pp cells on BOTH windows, AND the conditional 20-day executable mean return has the predicted sign on both
windows. Report the count of |S| > 1pp cells; if fewer than 6, state that the test is underpowered and publish anyway. The first paragraph
of your note answers: "may the memo claim an expectations edge on the guide?" — yes / no / underpowered.

## Outputs
`alpha_a/` code and outputs; registry files `alpha-a__guide_gap_next_q` (PIT rows) and the live row; one figure (S vs actual gap);
note `05_backtests/ALPHA_A_GUIDE_SURPRISE.md`.

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
