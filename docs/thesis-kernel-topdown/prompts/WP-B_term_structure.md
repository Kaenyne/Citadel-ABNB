# WP-B — Thesis B — kernel term structure vs FY consensus

**Lane:** Krish lane · **Effort:** 2 days (after WP-A) · **Needs from outside the repo:** better with the LSEG estimates history (WP-G1); workable with the register as is, flagged

You are a contributor to the Citadel-ABNB pitch (Airbnb, 2026 Citadel Intercollegiate Stock Pitch Competition; memo due
2 Oct 2026; finals 22–24 Oct; next print 5 Nov). This work package is part of the **kernel / top-down thesis**: Airbnb's
revenue is mostly *converted* from bookings that are already printed, the guide is that revenue over a shrinking cushion,
and the Street misreads the composition of growth as demand. Read `docs/thesis-kernel-topdown/README.md` and
`01_CONTEXT.md` first (10 minutes), then this file.

## The task
**Claim.** At every print the kernel gives a revenue range for q+1 (⅔ of the base printed) and q+2 (⅓ printed). Consensus for those
quarters and for the fiscal year drifts toward the kernel between prints; the drift is a forecastable revision, and the multiple follows
forward growth (+0.48 turns per point).

**Build `alpha_b/`:** at each print date, T = kernel_FY − FY_consensus, where kernel_FY = printed quarters + kernel(q+1) + kernel(q+2)
+ seasonal naive for anything beyond; FY consensus from the vintage register (thin before 2024 — flag every date where the vintage is
older than 30 days). Targets: FY consensus revision over 30 / 60 / 90 days; realised FY revenue; 20- and 60-day executable returns.
Baselines: no revision (random walk); last revision continues. Also produce the current term structure: kernel ranges for 4Q26 and
1Q27 with the kernel-weight band (w = 0.33 … ⅔) against today's stamped consensus.

## Pass line (pre-registered — write it in your note before running)
T predicts the sign of the 60-day FY revision in ≥ 70% of dates with |T| > 0.5%, and corr(T, 60-day revision) > 0.4 on both windows.
State the honest n for the return leg (≈10).

## Outputs
`alpha_b/`; registry `alpha-b__fy_gap_at_print`; note `05_backtests/ALPHA_B_TERM_STRUCTURE.md` with the current term-structure table.

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
