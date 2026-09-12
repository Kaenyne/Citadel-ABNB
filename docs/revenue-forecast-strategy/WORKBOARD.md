# WORKBOARD — claim before you start, update when you stop

External contributors: the paste-ready prompt for each WP is in `docs/thesis-kernel-topdown/prompts/`; setup in `02_SETUP.md`.

One row per work package (IDs and specs in `AGENT_BRIEF.md` §5). To claim: set `status=claimed`, put your
session/agent name and branch, commit the board on your branch (or just save it if you are on Theo's machine).
If a package is `claimed` or `in-progress` by someone else, pick another or coordinate — never work the same
package in parallel. When done: `status=done`, link the note, re-run `harness/score.py` if you registered anything.

Status values: `open` · `claimed` · `in-progress` · `blocked (reason)` · `done` · `human (needs a person)`

| WP | Title | Lane | Status | Owner / agent | Branch | Started | Last update | Output |
|---|---|---|---|---|---|---|---|---|
| WP-X | Regional kernel + origin–destination FX exposure matrix (R-engine `exposure.csv`); regional recompute of the FX carried through the kernel — supersedes the consolidated basket | Krish (O–D travel analysis) | claimed (v2 resumption; waiting for gates) | Codex / Lane 1 parent | codex/lane1-full | 2026-09-12 | 2026-09-12 | [Lane 1 resumed log](05_backtests/LANE1_RUN_LOG_v2.md) |
| WP-R | Regional refresh using public arrivals and regional revenue inputs | Krish | claimed (v2 resumption; waiting for gates) | Codex / Lane 1 parent | codex/lane1-full | 2026-09-12 | 2026-09-12 | [Lane 1 resumed log](05_backtests/LANE1_RUN_LOG_v2.md) |
| WP-K0 | Kernel engine module `kernel_engine_v2/` (PIT λ, kernel guide, term structure, control chart) — spine for Lane 1 | Krish | done (v2 Gate 1 passed) | Codex / Lane 1 parent | codex/lane1-full | 2026-09-12 | 2026-09-12 | [K0 v2](05_backtests/K0_KERNEL_ENGINE_v2.md) |
| WP-V | Valuation reconciliation page for decision WP-H (+0.48 turns/pt → FY27 band → price band vs football field vs branch analogues) | Krish | claimed (v2 resumption; waiting for gates) | Codex / Lane 1 parent | codex/lane1-full | 2026-09-12 | 2026-09-12 | [Lane 1 resumed log](05_backtests/LANE1_RUN_LOG_v2.md) |
| WP-H | Direction + target reconciliation (football field vs branch analogues; adopt ex-NA lap?) | all | **human** | Theo · Krish · Jessie | — | — | 2026-09-11 | one line in the card + `05_backtests/H_DIRECTION_DECISION.md` |
| WP-G0 | LSEG Workspace self-registration via UF | Theo | **human** | Theo | — | — | 2026-09-11 | login works at workspace.refinitiv.com/web |
| WP-G1 | LSEG estimates history export → vintage register (ABNB, NCLH, BKNG, EXPE) | Theo | blocked (WP-G0) | — | — | — | 2026-09-11 | `L0/consensus_history_loader.py` run; register rows |
| WP-A | Thesis A backtest — kernel guide vs Street at 14 guide dates, executable returns | Krish | done (underpowered; Gate 2 clean) | Codex / Lane 1 parent | codex/lane1-full | 2026-09-12 | 2026-09-12 | [A guide surprise](05_backtests/ALPHA_A_GUIDE_SURPRISE.md) |
| WP-F | Wire RNPL as a variable (u, L, re-based nights, λ chart, funds-payable score line) + FX-confound check | Theo | open | — | — | — | 2026-09-11 | `rnpl_v2/`, `05_backtests/ALPHA_F_RNPL.md` |
| WP-E1 | Thesis E — NCLH advance-ticket-sales kernel | Jessie | open | — | — | — | 2026-09-11 | `05_backtests/ALPHA_E_NCLH.md` |
| WP-B | Thesis B′ — kernel term structure vs FY-guide revisions (free-data variant; FY consensus after WP-G1) | Krish | claimed (v2 resumption; waiting for gates) | Codex / Lane 1 parent | codex/lane1-full | 2026-09-12 | 2026-09-12 | [Lane 1 resumed log](05_backtests/LANE1_RUN_LOG_v2.md) |
| WP-C1 | Calendar pickup ≤ 90 days from consecutive Inside Airbnb dumps → booked-GBV feature | Theo | blocked (September dumps, mid/late Sep) | — | — | — | 2026-09-11 | `pickup_v1/`, `05_backtests/ALPHA_C1_PICKUP.md` |
| WP-C2 | Macro / arrivals pulls (NTTO, Eurostat, JNTO, INE, DATATUR, ISTAT, STR weekly, CPI) → covariates | Theo | open | — | — | — | 2026-09-11 | `data/processed/forecast_methods/macro_pulls/` + manifest |
| WP-C3 | Retarget the 598 alt-data features + stays index at booked GBV and at the residual R | Krish | claimed (v2 resumption; waiting for gates) | Codex / Lane 1 parent | codex/lane1-full | 2026-09-12 | 2026-09-12 | [Lane 1 resumed log](05_backtests/LANE1_RUN_LOG_v2.md) |
| WP-D | λ control chart + backlog split into the pre-registration card (items F1–F4) | Krish | claimed (v2 resumption; waiting for gates) | Codex / Lane 1 parent | codex/lane1-full | 2026-09-12 | 2026-09-12 | [Lane 1 resumed log](05_backtests/LANE1_RUN_LOG_v2.md) |
| WP-E2 | Thesis E — BKNG / EXPE deferred merchant bookings kernel | Jessie | open (after E1) | — | — | — | 2026-09-11 | `05_backtests/ALPHA_E_OTA.md` |
| WP-I | Memo v1 (direction committed, kernel → composition → flip rule; one chart, one table) | Writer | blocked (WP-H) | — | — | — | 2026-09-11 | `deck/drafts/memo_v1.md` |
| WP-J | Re-score + refresh `SCOREBOARD_v3.md` after new registrations; verify loop | any | open (recurring) | — | — | — | 2026-09-11 | `05_backtests/SCOREBOARD_v3.md` |
| WP-K | Ingest the September Inside Airbnb batch (+ unlisted Aug 2026 batch, 86 markets); refresh reviews index and party-size series | Theo | blocked (batch not out) | — | — | — | 2026-09-11 | manifests; refreshed E / I outputs |
| WP-L | Airbnb policy monitor (RNPL, fees, cancellation) — weekly fetch + diff, dated log | Theo | open (small) | — | — | — | 2026-09-11 | `data/manifests/policy_monitor.log` |
| WP-M | Consensus re-stamp weekly + 2–3 Nov (Zacks nights/ADR/GBV) | Theo | open (recurring) | — | — | — | 2026-09-11 | vintage register rows |
| WP-N | Fee-panel runs 14/16/18 Sep — measure panel overlap on 16 Sep; θ DiD after 18 Sep | Jessie | scheduled (launchd) | — | — | — | 2026-09-11 | `05_backtests/N_THETA_DID.md` |
| WP-O | ToS decisions: fee-inclusive quote route; Experiences/Services counts scrape; AirDNA purchase | all | **human** | team | — | — | 2026-09-11 | decision logged here |
| WP-P | Card freeze ABNB-INT-v1 (26 Sep) and 5 Nov score sheet | Writer | blocked (WP-H, WP-F, WP-A) | — | — | — | 2026-09-11 | `PREREG_ABNB-INT-v1.md` signed |

## Done (11 Sep 2026)

| WP | What | Note |
|---|---|---|
| A1 | Consensus stamped, all vendors, vintage register 127 → 167 rows | `05_backtests/A1_consensus_vintages.md` |
| A2 | Inside Airbnb daily capture live (360/360 files, launchd 06:00) | `05_backtests/A2_ia_capture.md` |
| A3 | Fee-deadline panels: dates sourced (S66–S71), 2,600-listing sample, dry run, launchd | `05_backtests/A3_fee_panels.md` |
| B1 | 3Q26 take rate reconciled: 18.14 %, sd 0.46, P(≥ 18.10) 0.53 | `05_backtests/B1_TAKE_RATE_RECONCILIATION.md` |
| B2 | Q4 guide as a distribution: $3,161M (80 % 3,012–3,312); P(below) 0.49 / 0.50 / 0.63 | `05_backtests/B2_Q4_GUIDE_EXHIBIT.md` |
| B3 | FY27 decomposition rebuilt multiplicatively; band +9.18–11.52 %; exploratory | `05_backtests/B3_FY27_DECOMPOSITION.md` |
| B4 | FX exhibit: 4Q26 +1.0pp (CS +0.3–2.2); observed-share triple; four-way table | `05_backtests/B4_FX_EXHIBIT.md` |
| C1 | Pre-registration card v1 with the 11 team decisions | `05_backtests/PREREG_ABNB-INT-v1.md` |
| C2 | Memo v0 (1,153 words) + exhibits; thesis draft | `deck/drafts/memo_v0_2026-09-11.md` |
| D1 | Scoreboard v2 narrative; hand-off message | `05_backtests/SCOREBOARD_v2.md`, `HANDOFF_MESSAGE_2026-09-11.md` |
| K1 | Kernel weights from the ledger; paid/unpaid/not-booked split; RNPL leakage; conditional ranges | `05_backtests/K1_KERNEL_WEIGHTS_AND_BACKLOG.md` |
| K2 | Kernel weights from booking lead times (Melbourne STR 2014–17) | `05_backtests/K2_KERNEL_FROM_LEAD_TIMES.md` |
