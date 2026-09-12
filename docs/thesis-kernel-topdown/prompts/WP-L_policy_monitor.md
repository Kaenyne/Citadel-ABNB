# WP-L — Airbnb policy monitor — RNPL, fees, cancellation

**Lane:** Theo lane · **Effort:** hours to set up; weekly after · **Needs from outside the repo:** internet; read-only public pages

You are a contributor to the Citadel-ABNB pitch (Airbnb, 2026 Citadel Intercollegiate Stock Pitch Competition; memo due
2 Oct 2026; finals 22–24 Oct; next print 5 Nov). This work package is part of the **kernel / top-down thesis**: Airbnb's
revenue is mostly *converted* from bookings that are already printed, the guide is that revenue over a shrinking cushion,
and the Street misreads the composition of growth as demand. Read `docs/thesis-kernel-topdown/README.md` and
`01_CONTEXT.md` first (10 minutes), then this file.

## The task
Write `analysis/src/acquisition/policy_monitor.py`: fetch ~10 public Airbnb pages weekly (Help Center 1857 and 4095; Resource Center 771 and
746; the Newsroom pages on Reserve Now Pay Later and cancellation policy; the host fee page; add others you find), store the text, diff against
the last capture, and append any change with date, URL and the changed sentences to `data/manifests/policy_monitor.log`. Polite rate, real
User-Agent, no login, no more than one request per page per run. Schedule weekly (cron / launchd) and document.

## Pass line (pre-registered — write it in your note before running)
First run stored; a deliberate test diff detected; schedule verified; every date the team cites for fees / RNPL has a log entry with the sentence.

## Outputs
`policy_monitor.py`; `data/manifests/policy_monitor.log`; note `05_backtests/L_POLICY_MONITOR.md`.

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
