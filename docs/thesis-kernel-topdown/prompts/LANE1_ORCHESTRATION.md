# LANE 1 — orchestration prompt (paste into a fresh Claude Code session at the repo root)

You are orchestrating Lane 1 (kernel, guide, valuation) of the Citadel-ABNB kernel thesis. Read, in this order and nothing
else first: `CLAUDE.md`, `docs/revenue-forecast-strategy/AGENT_BRIEF.md` §1–§3 and §6–§8, `docs/thesis-kernel-topdown/03_NUMBERS_CHEATSHEET.md`,
`analysis/src/forecast_methods/harness/README.md`. Then run the plan below with the Workflow tool (deterministic phases) or with
background agents. Budget tier is set at the top; do not exceed it without asking.

## Budget tier (choose one before launching)

- **CORE (~2M subagent tokens, fits ~20% of a Max weekly cap):** K0 → {A, B′, V, D} in parallel → 1 refuter on A → close. No fix loop beyond one pass.
- **FULL (~7–8M):** CORE + R + C3 + build/verify/fix/re-verify on every package + 3 refuters per headline claim.

Token discipline for every agent: read ONLY the files named in its brief; write long content to disk; return a compact structured
summary (no file paths inside JSON strings — an apostrophe in this repo's path breaks JSON); Sonnet for arithmetic and verification,
Opus for estimation and refutation.

## Phase 0 — K0 kernel engine (Opus build → Sonnet verify; barrier)

Build `analysis/src/forecast_methods/kernel_engine_v1/` (copy from `kernel_lambda/` and `kernel_phi_v2/`; never edit them) exposing
`pit_lambda(season, as_of, variant)`, `kernel_forecast(q, as_of)`, `kernel_guide(q, as_of, cushion='median'|'mean')`,
`term_structure(as_of)`, `control_chart(as_of)`. λ variants: same-season mean ex-COVID, last-3 same-season, EW; choose by LOO on W1
and FREEZE the choice in the README. Uncertainty by block bootstrap of within-season λ residuals ⊕ cushion sd, plus conformal-lite from
walk-forward residuals (state n_cal). Term structure q+2 uses the ledger GBV nowcast (RNPL-corrected unearned fees; K1) with its interval.
Acceptance: the 12-cell λ table reproduces to 2dp (Q3 17.391/17.145/17.182; Q4 11.946/12.117/12.026); pytest green; runs in seconds.
Verifier: re-run from clean, recompute six numbers, check no future data enters any `as_of` call.

## Phase 1 — packages (parallel; each Opus build → Sonnet verify; fix once only in FULL)

- **A** — `docs/thesis-kernel-topdown/prompts/WP-A_guide_surprise.md`, but import K0 instead of re-deriving λ. Statistics: Wilson interval
  on the hit-rate, permutation test on sign labels, ridge-shrunk slope of actual gap on S with block-bootstrap CI, conditional 20-day
  executable returns with bootstrap CI; both windows; live 5 Nov row against the three stamped anchors. Pass line as in the prompt.
- **B′** — `WP-B_term_structure.md` reformulated for free data: targets are (i) the next FY-guide revision by management
  (`data/processed/overnight/02_fy_guide_revisions.csv`) and (ii) next-quarter consensus where a vendor-stamped value exists; the FY-consensus
  leg is a one-line swap when LSEG history arrives (WP-G1). Same statistics as A.
- **V** — Sonnet. One page for decision WP-H: reproduce the +0.48 turns/pt relation point-in-time from the overnight WS12 files; map the
  FY27 growth band (+9.18 to +11.52%) → multiple band → price band using the model's FY27E EBITDA; the football field at 13.5/16.5/18.5x;
  the memo v0 branch analogues; positioning (short interest, ratings, target dispersion, refreshed with yfinance). No recommendation —
  the side-by-side and the arithmetic. Output `05_backtests/V_VALUATION_RECONCILIATION.md`.
- **D** — Sonnet. `WP-D_lambda_card.md` (card rows for λ thresholds and the backlog split; new addendum file).
- **R** (FULL only) — regional reconciliation refresh: national arrivals as covariates for the L1 latent nights, shrink to 10-K annual anchors,
  bootstrap the identity residuals; re-run the FY27 attribution block with intervals. New folder `l1_reconciliation_v3/`.
- **C3** (FULL only) — `WP-C3_gbv_features.md` on the ledger features only (no calendar pickup yet).

## Phase 2 — refute (CORE: one Opus refuter on A's headline claim; FULL: 3 per headline claim with lenses vintage/PIT, power & multiple
comparisons, economic mechanism; majority rules)

The refuter reads only the package note, its registry files and the raw inputs; it must rebuild the central number independently,
try to construct a vendor-splice or look-ahead that would produce the same result, count the specs that were tried, and return
refuted / survived / partially with the attack that worked.

## Phase 3 — close (Sonnet)

Run `harness/score.py`; write `05_backtests/LANE1_MEMO_READY_CLAIMS.md`: for each surviving claim the exact sentence the memo may use,
the number, the evidence file, the caveat, and the window results; list refuted claims separately. Update `WORKBOARD.md`. Do not commit;
report the branch state.

## Rules that travel with every agent

Copy-never-overwrite (new folders, new registry method names, new notes) · consensus only from the vintage register with vendor + timestamp ·
W1 and W2 both · pre-registered pass lines · baselines: naive/AR(1), trailing-4, guide × (1 + cushion), vintage-stamped Street ·
nothing from the kill list (`AGENT_BRIEF.md` §6) · no scraping · no licensed data in git · agents do not make the eleven team decisions.
