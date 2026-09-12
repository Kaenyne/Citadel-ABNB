# CODEX — Lane 1 end to end, full subagentic run (paste verbatim as the first message)

You are the PARENT ORCHESTRATOR for Lane 1 (kernel, guide, valuation, regional FX) of the Citadel-ABNB kernel thesis. Deliver the
whole lane end to end: spawn a subagent for every independent package, gate on the two results everything else depends on, refute
every headline claim adversarially, push checkpoints as you go, and close with one pushed branch and one PR. `AGENTS.md` at the repo
root is loaded automatically — obey it. Everything you need is in git or on the public internet; nothing requires Theo's machine.
Never ask a human mid-run except for the STOP conditions at the end.

## 0. Get the repo and set up (you; ~10 minutes)

```bash
# fresh machine:
git clone https://github.com/Kaenyne/Citadel-ABNB.git && cd Citadel-ABNB
# existing clone:
cd Citadel-ABNB && git fetch --all --prune
# branch: use main if PR #48 has merged (git log --oneline -1 origin/main should show it); otherwise the kit branch
git checkout main && git pull || true
git ls-remote --heads origin theo/thesis-kernel-topdown | grep -q . && git merge-base --is-ancestor origin/theo/thesis-kernel-topdown origin/main \
  || { git checkout theo/thesis-kernel-topdown && git pull; }
git checkout -b codex/lane1-full

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt pymc arviz scikit-learn pyarrow linearmodels lightgbm duckdb yfinance
```

## 0b. Data-access check — must be all green before anything is spawned

```bash
# 1) every file the Lane-1 briefs read must exist in the checkout
for f in \
  data/processed/overnight/02_kpi_panel_quarterly.csv data/processed/overnight/02_kpi_panel_long.csv \
  data/processed/overnight/02_guidance_ledger.csv data/processed/overnight/02_guidance_cushion_series.csv \
  data/processed/overnight/02_fy_guide_revisions.csv data/processed/overnight/16_consensus_at_print_merged.csv \
  data/processed/overnight/04_consensus_at_print.csv data/processed/abnb_earnings_reactions.csv data/processed/abnb_daily_close.csv \
  data/processed/overnight/10_xbrl_revenue_geography.csv data/processed/overnight/10_regional_panel_quarterly.csv \
  data/processed/overnight/10_regional_forecast.csv data/processed/overnight/10_fx_daily.csv data/processed/overnight/10_fx_basket.csv \
  data/processed/overnight/10_regional_fx_passthrough.csv data/processed/overnight/05_crossborder_share.csv \
  data/processed/overnight/08_feature_tests_all.csv data/processed/overnight/12_exit_multiple_recommendation.csv \
  data/processed/overnight/12_peer_multiples.csv data/processed/overnight/13_valuation_summary.csv data/processed/overnight/13_model_annual.csv \
  data/processed/overnight2/D/D1_rnpl_cohort_scenarios.csv data/processed/nights_baseline_reconciliation.csv \
  data/processed/abnb_backlog_indicators.csv data/processed/adr/01_regional_annual.csv data/processed/adr/04_regional_quarterly.csv \
  data/processed/forecast_methods/L0/L0_vintage_register.csv data/processed/forecast_methods/L0/L0_exact_regional_revenue.csv \
  data/processed/forecast_methods/L0/L0_interval_observations.csv data/processed/forecast_methods/kernel_phi_v2 \
  data/processed/forecast_methods/l1_reconciliation_v2 data/processed/forecast_methods/fx_lag_v2 data/processed/forecast_methods/registry \
  analysis/src/forecast_methods/harness/README.md analysis/src/forecast_methods/kernel_lambda/run.py \
  docs/thesis-kernel-topdown/lane1/K0_KERNEL_ENGINE.md docs/thesis-kernel-topdown/lane1/X_REGIONAL_KERNEL_OD_FX.md \
  docs/revenue-forecast-strategy/AGENT_BRIEF.md docs/revenue-forecast-strategy/WORKBOARD.md ; do
  [ -e "$f" ] && echo "ok       $f" || { echo "MISSING  $f"; MISSING=1; }
done; [ -z "$MISSING" ] || { echo "STOP: files missing — report the list"; }

# 2) the data must load and the spine must reproduce
python -m pytest analysis/src/forecast_methods/harness/tests analysis/src/forecast_methods/L0 -q   # expect: 47 passed
python analysis/src/forecast_methods/kernel_lambda/run.py                                          # expect: "acceptance test: PASS on all 12 cells"
python - <<'EOF'
import sys, pathlib, pandas as pd
sys.path.insert(0, str(pathlib.Path("analysis/src/forecast_methods").resolve()))
from harness import load_calendar, load_targets, load_registry
from L0 import l0
print("calendar rows", len(load_calendar()), "| targets rows", len(load_targets()), "| registry files", load_registry()["method"].nunique(), "methods")
r = l0.load_vintage_register(); print("vintage register rows", len(r), "| LSEG 6 Aug Q3 =", l0.pit_consensus("revenue","2026Q3","2026-08-07",role="pre_guide")["value"])
print("72 exact regional cells:", len(pd.read_csv("data/processed/forecast_methods/L0/L0_exact_regional_revenue.csv")))
EOF

# 3) network and optional tools (decides the mode for sub-V, sub-R, sub-X)
curl -s -m 10 -o /dev/null -w "FRED %{http_code}\n"  "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DTWEXBGS"
curl -s -m 10 -o /dev/null -w "NTTO %{http_code}\n"  "https://www.trade.gov/i-94-arrivals-program"
curl -s -m 10 -o /dev/null -w "Eurostat %{http_code}\n" "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/tour_occ_nim?format=JSON&lastTimePeriod=1"
python -c "import yfinance as yf; print('yfinance', yf.Ticker('ABNB').fast_info['last_price'])" || echo "yfinance offline"
command -v Rscript >/dev/null && echo "Rscript available (X may cross-check the R engine)" || echo "no Rscript (X replicates the engine in Python)"
```
Record the check output verbatim as the first section of `docs/revenue-forecast-strategy/05_backtests/LANE1_RUN_LOG.md`, plus the branch
and commit you started from. Any MISSING file, a test count other than 47, or a failed acceptance table → STOP and report. Network
codes other than 200 are not a stop: note them and run sub-V / sub-R / sub-X in offline mode.

Then read, in this order and nothing else yet: `docs/thesis-kernel-topdown/lane1/README.md` · `docs/thesis-kernel-topdown/03_NUMBERS_CHEATSHEET.md` ·
`analysis/src/forecast_methods/harness/README.md` · `docs/revenue-forecast-strategy/AGENT_BRIEF.md` §3 and §6. Claim the Lane-1 rows
(K0, A, B′, V, D, R, C3, X) in `docs/revenue-forecast-strategy/WORKBOARD.md` with today's date, commit that, and push the branch:
`git push -u origin codex/lane1-full`.

## 1. Gate 1 — K0, run by YOU (no subagent)

Follow `docs/thesis-kernel-topdown/lane1/K0_KERNEL_ENGINE.md` exactly. Gate 1 passes only if the 12-cell λ table reproduces to 2dp
(Q3 17.391 / 17.145 / 17.182; Q4 11.946 / 12.117 / 12.026), the new module's pytest is green, every function refuses data printed on or after
its `as_of`, AND the regional-ready interface exists (per-region GBV frame in; consolidated = sum). Fail → STOP and report.
Pass → **checkpoint: commit and push** (`git add analysis/src/forecast_methods/kernel_engine_v1 data/processed/forecast_methods/kernel_engine_v1 docs/revenue-forecast-strategy/05_backtests/K0_KERNEL_ENGINE.md docs/revenue-forecast-strategy/05_backtests/LANE1_RUN_LOG.md && git commit -m "K0 kernel engine" && git push`).

## 2. Gate 2 — A, one subagent, alone

Spawn `sub-A` with exactly one file: `docs/thesis-kernel-topdown/lane1/A_GUIDE_SURPRISE.md`. When it returns, YOU check its note for: the
pass line written BEFORE results; hit-rate with Wilson interval and cell counts on BOTH windows W1 and W2; vendor + timestamp on every
consensus value and no September-2026 value used at a historical date; executable `open_*` returns only; a one-word verdict
(pass / fail / underpowered) in the first paragraph; K0 imported, λ not re-derived. Any miss → send `sub-A` back once with the specific
defect; a second miss → STOP and report. A clean negative passes the gate. Pass → **checkpoint: commit and push**.

## 3. Parallel packages — spawn all six at once, one brief each

Each subagent receives exactly one brief and nothing else; writes only its own new folder, its own new registry method name and its own
new note; does not run `score.py`; does not touch `harness/`, `L0/` (append-only + dated backup), another package or any frozen file.

| subagent | brief | internet |
|---|---|---|
| `sub-B`  | `docs/thesis-kernel-topdown/lane1/B_TERM_STRUCTURE.md` | no |
| `sub-V`  | `docs/thesis-kernel-topdown/lane1/V_VALUATION_RECONCILIATION.md` | yes (yfinance) |
| `sub-D`  | `docs/thesis-kernel-topdown/lane1/D_LAMBDA_CARD.md` | no |
| `sub-R`  | `docs/thesis-kernel-topdown/lane1/R_REGIONAL_REFRESH.md` | yes (NTTO / Eurostat / national arrivals) |
| `sub-C3` | `docs/thesis-kernel-topdown/lane1/C3_GBV_FEATURES.md` | no |
| `sub-X`  | `docs/thesis-kernel-topdown/lane1/X_REGIONAL_KERNEL_OD_FX.md` | yes (arrivals) — **priority**: its regional FX recompute supersedes B4 |

If one fails, re-spawn it once with the failure text appended to its brief; twice → log it and continue. In offline mode `sub-V`, `sub-R`
and `sub-X` deliver the offline parts and say so in their notes. When all six have returned → **checkpoint: commit and push**.

## 4. Refuters — three per headline claim, distinct lenses, majority rules

For each returned package's ONE proposed memo sentence (A, B′, R, V, X), spawn three subagents with
`docs/thesis-kernel-topdown/lane1/REFUTER.md` plus the filled fields PACKAGE, CLAIM and LENS ∈ {vintage, power, mechanism}. They read only
the package note, its registry files and the raw inputs, and return refuted / survived / partially with ≥ 5 explicit attacks. A claim
survives on 2-of-3. For X: the vintage lens checks that the O–D matrix and exposure weights use only data available at each historical
guide date; the mechanism lens checks whether the regional recompute changes the 3Q26 / 4Q26 FX conclusion or merely re-weights the same
basket. Record every verdict in the run log. → **checkpoint: commit and push**.

## 5. Close — you, no subagent (`docs/thesis-kernel-topdown/lane1/CLOSE.md`)

1. `python analysis/src/forecast_methods/harness/score.py`; write `05_backtests/SCOREBOARD_v3.md` (new file) if any leader changed; label
   empty-ratio rows "no baseline exists" and same-ten-quarter survivors "vacuous".
2. Write `05_backtests/LANE1_MEMO_READY_CLAIMS.md`: for every claim that survived 2-of-3 — the exact memo sentence, the number, the evidence
   file, the caveat, W1 and W2 results; refuted and partial claims in a separate section with the attack that worked; state explicitly
   whether X changed the FX conclusion and, if so, mark B4's numbers superseded.
3. Update `WORKBOARD.md` (status, note links); finish `LANE1_RUN_LOG.md` (totals: subagents spawned, tokens, wall time).
4. **Final push and PR:**
```bash
git add -A analysis/src/forecast_methods data/processed/forecast_methods docs/revenue-forecast-strategy
git status --short | grep -v -E "^(A|M) " && echo "review any unexpected line above before committing"
git commit -m "Lane 1 full: kernel engine, guide surprise, term structure, valuation page, regional refresh, GBV features, regional kernel + O-D FX, refuters"
git push -u origin codex/lane1-full
gh pr create --base main --head codex/lane1-full --title "Lane 1 full: kernel engine, guide surprise, term structure, valuation page, regional refresh, GBV features, regional kernel + O-D FX, refuters" --body-file docs/revenue-forecast-strategy/05_backtests/LANE1_MEMO_READY_CLAIMS.md \
  || echo "gh unavailable — open the PR at https://github.com/Kaenyne/Citadel-ABNB/compare/main...codex/lane1-full"
```
   The PR body must also carry, per package: pass line, result, the three refuter verdicts, tokens; the Gate 1 and Gate 2 evidence; anything
   left undone and why. Never commit licensed data, raw stores, `.venv`, or `__pycache__` (they are gitignored; check `git status` first).

## 6. Budget and fallback

Expected ≈ 7.5–8.5M tokens (K0 0.3 · A 0.35 · B′ 0.3 · V 0.2 · D 0.1 · R 0.4 · C3 0.35 · X 0.5 · 15 refuters ≈ 3.0 · close 0.15 + orchestration).
If quota runs short at any point, complete in THIS order, then push whatever exists and open the PR: K0 → A → 3 refuters on A → X →
3 refuters on X → CLOSE. Because you push at every checkpoint, a hard cut loses at most one stage.

## 7. Hard constraints (from AGENTS.md; repeated because they are where runs go wrong)

Copy, never overwrite (frozen: `harness/`, `L0/` append-only + dated backup, `data/processed/overnight/20_frozen_q3_2026.csv`,
`research/thesis.md`, every existing package and note) · point-in-time only (consensus from `L0_vintage_register.csv` with vendor +
timestamp before the date; refit at guide dates; both windows; letter integers as ±0.5 intervals; executable `open_*` returns) ·
pre-register every pass line · no scraping · no credentials · no licensed data in git · no commits to `main` · you do NOT make the
eleven team decisions (AGENT_BRIEF §3) and do NOT quote the kill list (§6) · portable commands only (`python` from `.venv`, repo root, `pathlib`).

## 8. STOP conditions (report and halt — do not improvise)

Any MISSING file in 0b · test count ≠ 47 · kernel acceptance not PASS · Gate 1 fails · Gate 2 fails twice · harness tests fail after any step ·
a subagent needs data that is not in git and not on the public internet · anything touching airbnb.com, a UF database or a licensed source.

Report back in this order: the 0b check output; Gate 1 evidence; A's verdict and its three refuter verdicts; X's verdict and whether it
changed the FX conclusion; the memo-ready claims file; confirmation that `codex/lane1-full` is pushed and the PR link; tokens and wall time.
