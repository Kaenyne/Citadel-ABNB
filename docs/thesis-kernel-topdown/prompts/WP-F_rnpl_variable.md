# WP-F — RNPL as a variable in the model and as thesis F

**Lane:** Theo lane · **Effort:** 1–2 days + Theo's review · **Needs from outside the repo:** nothing — filings text is in the repo notes; fetch the 10-K/10-Q from EDGAR if you need the notes

You are a contributor to the Citadel-ABNB pitch (Airbnb, 2026 Citadel Intercollegiate Stock Pitch Competition; memo due
2 Oct 2026; finals 22–24 Oct; next print 5 Nov). This work package is part of the **kernel / top-down thesis**: Airbnb's
revenue is mostly *converted* from bookings that are already printed, the guide is that revenue over a shrinking cushion,
and the Street misreads the composition of growth as demand. Read `docs/thesis-kernel-topdown/README.md` and
`01_CONTEXT.md` first (10 minutes), then this file.

## The task
**Objective.** Put Reserve Now, Pay Later into the model explicitly and pre-register its tells; resolve the open disagreement about which
balance-sheet line carries the FX confound.

**Read first:** `05_backtests/K1_KERNEL_WEIGHTS_AND_BACKLOG.md` (parts B–C), `research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md`
+ `analysis/src/rnpl_balance_sheet_bridge.py`, `research/notes/overnight2/D_rnpl-statement-ledger-and-cohort-scenarios.md` +
`data/processed/overnight2/D/D1_rnpl_cohort_scenarios.csv`, `docs/RNPL_HANDOFF.md`, `05_backtests/tracker-backlog.md` (why the restated
unearned-fees pin is circular — never use it).

**Build `rnpl_v2/`:**
1. Paid backlog = unearned fees + funds payable; seasonal coverage norms (2022–1H25); the paid / booked-unpaid / not-yet-booked split by season.
2. Re-derive u (unpaid RNPL share) and m (single-fee migration share) by the joint solve; publish the range and the excess-unpaid series.
3. Resolve decision D-06: from the FY2025 10-K and 2Q26 10-Q notes, which of unearned fees / funds payable is translated at historical rates,
   which at period-end, and which is affected by the host-only fee. Quote the sentences. K1 says unearned fees is FX-clean and funds payable
   carries the confound; Theo's note says the reverse. Decide with evidence.
4. Kernel with leakage: revenue_q = c_s Σ φ_k GBV_{q−k} (1 − L_q), L = RNPL share of GBV × differential cancellation rate from the D1 grid;
   λ control chart with seasonal bands and the 5 Nov thresholds (17.09 / 16.93%); historical false-alarm rate.
5. Nights as a switchable input: team baseline (+9.9 / +8.9), Theo re-base (+9.3 / +7.6), ex-NA lap (Q4 8.0–8.2); report 3Q26 / 4Q26 revenue under each.
6. Thesis F write-up: the setup (reported GBV and nights ran ~4 points ahead of the paid backlog from 3Q25; multiple 13.3x → 18.2x), the
   tells (λ; funds payable y/y +5–11% = on schedule; cancellation language; bundle figure restated; Q4 nights word), and ONE refutation
   condition replacing the two incompatible versions in decision D-10.

## Pass line (pre-registered — write it in your note before running)
The excess-unpaid series reproduces (+2.0 / +8.1 / +9.7pp); the λ chart's false-alarm rate is published; the model runs under all three nights
inputs; D-06 has a documented, quoted answer; D-10 has one refutation condition.

## Outputs
`rnpl_v2/`; registry `rnpl-v2__revenue_next_q` (three nights variants; PIT where possible); note `05_backtests/ALPHA_F_RNPL.md`; proposed
card rows F1–F4 in the note (do not edit the card).

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
