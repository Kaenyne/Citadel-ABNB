# CODEX HAND-OFF — Lane 1 CORE (paste this as the first message in a Codex session opened at the repo root, branch `theo/thesis-kernel-topdown`)

You are Codex working in the Citadel-ABNB repository. `AGENTS.md` at the root is loaded automatically — obey it. Your job is the
**Lane 1 CORE** tier of the kernel thesis: build the kernel engine, run the guide-surprise and term-structure tests, prepare the
valuation reconciliation page and the λ card rows, refute the headline claim once, and write the memo-ready claims file.
Work sequentially in the order below; each step's full spec is in the named file — read it, then execute. Do not read anything
else unless a spec names it (token discipline). No browser, no MCP, no scraping, no credentials, no commits to `main`.

Setup first (5 min): `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt pymc arviz scikit-learn pyarrow linearmodels lightgbm duckdb`
then `python -m pytest analysis/src/forecast_methods/harness/tests -q` and `python analysis/src/forecast_methods/kernel_lambda/run.py`
— the λ table must print Q3 17.391/17.145/17.182 and Q4 11.946/12.117/12.026. If not, stop and report.

Then claim your rows in `docs/revenue-forecast-strategy/WORKBOARD.md` (they are pre-marked "claimed · Codex (Lane 1 core)"; add the date).

## Steps (do them in order; each writes a NEW folder and a NEW note; never edit an existing package or note)

1. **K0 kernel engine** — spec: `docs/thesis-kernel-topdown/prompts/LANE1_ORCHESTRATION.md` §"Phase 0".
   Output `analysis/src/forecast_methods/kernel_engine_v1/` + `docs/revenue-forecast-strategy/05_backtests/K0_KERNEL_ENGINE.md`.
   Acceptance: λ table to 2dp, pytest green, every function refuses future data for its `as_of`.
2. **A guide surprise** — spec: `prompts/WP-A_guide_surprise.md` (import K0; do not re-derive λ). Statistics: Wilson interval, permutation
   test on signs, ridge-shrunk slope with block-bootstrap CI, conditional 20-day executable returns; both windows; the live 5 Nov row.
   Pass line is in the prompt — write it in the note before running.
3. **B′ term structure** — spec: `prompts/WP-B_term_structure.md` with the free-data reformulation in `LANE1_ORCHESTRATION.md` §"Phase 1 B′"
   (targets: management's next FY-guide revision from `data/processed/overnight/02_fy_guide_revisions.csv`, and next-quarter consensus
   where a vendor-stamped value exists). Same statistics.
4. **V valuation reconciliation** — spec: `LANE1_ORCHESTRATION.md` §"Phase 1 V". One page, arithmetic only, no recommendation.
   Refresh prices with `yfinance` (already in requirements). Output `05_backtests/V_VALUATION_RECONCILIATION.md`.
5. **D λ card rows** — spec: `prompts/WP-D_lambda_card.md`. Output `05_backtests/D_CARD_ADDENDUM_LAMBDA.md`.
6. **Refute A once** — a fresh pass, as if you were a hostile econometrician: rebuild A's central hit-rate independently from the registry
   CSVs and the guide ledger; try to produce the same result with a vendor splice or a look-ahead; count how many specifications were tried;
   write `05_backtests/REFUTE_A.md` with verdict refuted / survived / partially and the attack that worked or failed.
7. **Close** — `python analysis/src/forecast_methods/harness/score.py`; write `05_backtests/LANE1_MEMO_READY_CLAIMS.md` (for each surviving
   claim: the exact sentence the memo may use, the number, the evidence file, the caveat, W1/W2 results; refuted claims listed separately);
   update `WORKBOARD.md` (status, note links); commit on your branch `codex/lane1-core` and open a PR against `main` titled
   "Lane 1 core: kernel engine, guide-surprise and term-structure tests, valuation reconciliation".

## What you must not do

Make any of the eleven team decisions in `AGENT_BRIEF.md` §3 (lay out options instead) · quote anything from the kill list (§6) ·
mix a current consensus value into a historical date (use `data/processed/forecast_methods/L0/L0_vintage_register.csv` with vendor + timestamp) ·
touch `harness/`, `L0/` (append-only with backup), `20_frozen_q3_2026.csv`, `research/thesis.md`, or any existing package ·
commit licensed data or raw stores.

## Report back (in the PR description and as your final message)

For A and B′: hit-rate with Wilson interval and cell counts on W1 and W2, permutation p, the slope CI, the conditional 20-day return with CI,
the live 5 Nov row; the verdict of REFUTE_A; the V page's price band from the FY27 growth band; anything you could not do and why.
Estimated cost: ~2M tokens across the seven steps; if you are running low, finish K0 + A + REFUTE_A + close first — that is the decision-relevant subset.

---

## Option FULL — run the whole of Lane 1 with Codex subagents, gated

If your quota allows (~7–8M tokens), run the FULL tier instead of CORE, with two gates and a fixed subagent map. Use subagents only for
independent packages; never for K0 or for the final close.

**Gate 1 — K0 must pass before anything else starts.** Run K0 yourself (no subagent). If the λ table does not reproduce to 2dp
(Q3 17.391/17.145/17.182; Q4 11.946/12.117/12.026) or pytest fails, STOP and report; do not spawn packages on a broken spine.

**Gate 2 — A must be clean before the expensive tail.** Spawn subagent A first (alone). Its note must state its pre-registered pass line
before results and end with a verdict of pass / fail / underpowered. If the note is missing the pass line, mixes consensus vintages, or
reports a hit-rate without cell counts and a Wilson interval, fix A before continuing.

**Subagent map after Gate 2 (parallel, one package each, own folder, own registry method name):**
- `sub-B`  → B′ term structure (spec: `WP-B_term_structure.md` + `LANE1_ORCHESTRATION.md` §Phase 1 B′)
- `sub-V`  → valuation reconciliation page (spec: `LANE1_ORCHESTRATION.md` §Phase 1 V)
- `sub-D`  → λ card rows (spec: `WP-D_lambda_card.md`)
- `sub-R`  → regional reconciliation refresh, new folder `l1_reconciliation_v3/` (spec: `LANE1_ORCHESTRATION.md` §Phase 1 R); needs internet
             for NTTO / Eurostat pulls — if the sandbox has no network, skip R and say so
- `sub-C3` → ledger features aimed at booked GBV and the residual R (spec: `WP-C3_gbv_features.md`, ledger features only)
Each subagent: reads only the files its spec names; writes its note with the §7 template; registers through the harness; does not run
`score.py` (you run it once at the close).

**Refuters (after the packages finish; three per headline claim from A, B′, R, V; each a separate subagent, reading only the package note,
its registry files and the raw inputs):** lens 1 vintage / point-in-time (construct a splice or look-ahead that reproduces the result);
lens 2 power and multiple comparisons (count specs tried; recompute the interval); lens 3 economic mechanism (is the effect the kernel
or something else). Majority rules per claim; write `05_backtests/REFUTE_<pkg>.md` with the three verdicts and the attacks.

**Close (you, not a subagent):** `score.py`; `LANE1_MEMO_READY_CLAIMS.md` with only majority-surviving claims; `WORKBOARD.md`; one PR
from `codex/lane1-full` against `main`. In the PR description list, per package: pass line, result, refuter verdicts, tokens spent.

**Budget fallback:** if you run short at any point, finish in this order and stop: K0 → A → REFUTE_A → close. Everything else can be
picked up later by a contributor from `docs/thesis-kernel-topdown/prompts/`.
