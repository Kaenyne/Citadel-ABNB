# Thesis kit — the recognition kernel (top-down) thesis on ABNB

**For contributors with a fresh clone.** Everything you need to take one work package of this thesis and run it
without talking to us first. Read this page (5 min), then `01_CONTEXT.md` (10 min), then `02_SETUP.md`, then the
prompt for your package under `prompts/`. Paste the prompt into Claude Code / Codex / your own head.

## The thesis in six sentences

1. Airbnb books GBV when a guest reserves and recognises revenue when the guest checks in — so **~60% of a quarter's
   revenue is already booked before the quarter starts** (~35% already paid; ~40% booked in-quarter).
2. Revenue converts from the printed bookings through a seasonal ratio λ that has moved **0.17 points in three years**
   (Q4): `revenue_q = λ_season × [⅔ GBV_{q−1} + ⅓ GBV_{q−2}]`, reproducible to two decimals from the KPI panel.
3. Airbnb's guide is that number over a shrinking cushion (+1.86%, sd 1.0pp); 19 of 19 midpoint beats are arithmetic.
   Once guided, guide × (1 + cushion) forecasts revenue to ~1% and **nothing we built beats it on both windows** — so the
   edge is never a level call on a guided quarter.
4. The Street forecasts nights × ADR × take rate as if the quarter were a blank page, misses the real guide by ~2.5pp,
   and reads the FY26→FY27 growth halving as demand when it is a **dollar lap + a product-bundle lap + a mix identity**.
5. **RNPL (Reserve Now, Pay Later, ~21% of GBV, no cash at booking, higher cancellations)** inflates booked GBV and nights
   before cash arrives, leaks from the kernel before check-in, and laps in 3Q26 (US) and 1Q27 (global). It is both a
   variable in the model and a thesis of its own (F).
6. The pitch (recommended: **short**, $182 → $157 base, bear $140–152, bull $205–215 with a written flip rule) is that
   an 18x multiple is paying for growth that is largely already determined and decelerating.

## What is done, what is open

Done (11 Sep 2026): the mechanism measured two ways (ledger regression K1; booking lead times K2), the 3Q26 live block
reconciled (B1), the 5 Nov Q4 guide as a distribution with vendor-stamped anchors (B2), FY27 decomposition rebuilt (B3),
FX exhibit and lag rule (B4), pre-registration card v1 with eleven team decisions (C1), memo v0 (C2), consensus vintages
stamped (A1), Inside Airbnb daily capture running (A2), fee-deadline price panels scheduled (A3).

Open — the packages in `prompts/` (see the table below). Three items are **human-only** and are not in `prompts/`:
the direction / target decision (WP-H), the LSEG Workspace registration (WP-G0), and the terms-of-service calls (WP-O).

## Work packages you can take

| Prompt | What | Lane | Effort | Needs outside the repo |
|---|---|---|---|---|
| `WP-A_guide_surprise.md` | does the kernel predict the guide better than the Street? (14 guide dates, executable returns) | Krish | 1 day | nothing |
| `WP-F_rnpl_variable.md` | RNPL as a variable (u, leakage L, λ chart, re-based nights) + thesis F tells | Theo | 1–2 days | nothing |
| `WP-E1_nclh_kernel.md` | does the kernel transfer to NCLH advance ticket sales? | Jessie | 3–5 days | free financials API |
| `WP-B_term_structure.md` | kernel FY range vs FY consensus → revision drift | Krish | 2 days | better with LSEG history |
| `WP-C1_calendar_pickup.md` | calendar pickup ≤ 90 days as a booked-GBV feature | Theo | 3–5 days | Inside Airbnb calendar dumps (public) |
| `WP-C2_macro_pulls.md` | NTTO / Eurostat / national arrivals / STR / CPI pulls with manifests | Theo | 1 day | internet |
| `WP-C3_gbv_features.md` | retarget the 598 alt-data features at booked GBV and the kernel residual | Krish | 2–3 days | WP-C1 optional |
| `WP-D_lambda_card.md` | λ thresholds and backlog split as card rows | Krish | hours | nothing |
| `WP-E2_ota_kernel.md` | BKNG / EXPE deferred merchant bookings | Jessie | 3–5 days / name | free financials API |
| `WP-G1_lseg_export.md` | point-in-time consensus history into the vintage register | Theo | half day | LSEG login (UF) |
| `WP-J_rescore.md` | re-score + SCOREBOARD_v3 after registrations | any | hours | nothing |
| `WP-L_policy_monitor.md` | weekly fetch + diff of Airbnb policy pages | Theo | hours | internet |
| `WP-M_consensus_stamp.md` | weekly consensus stamps; 2–3 Nov nights / ADR / GBV | Theo | 30 min | free API |
| `WP-N_theta_did.md` | pass-through θ from the fee-deadline panels (after 18 Sep) | Jessie | 2 days | capture CSVs (pushed by Theo) |

Claim your package in `docs/revenue-forecast-strategy/WORKBOARD.md` before starting; one package per person or agent.

## Files in this kit

- `01_CONTEXT.md` — mechanism, definitions, what is established with sources, the eleven open decisions, the kill list.
- `02_SETUP.md` — clone, venv, smoke test (the λ table must reproduce), where big data lives and what you can do without it.
- `03_NUMBERS_CHEATSHEET.md` — every number a contributor may quote, with its source note.
- `04_DATA_MAP.md` — per package: the exact files it reads, whether they are in git, and how to fetch what is not.
- `prompts/` — one paste-ready prompt per package (rules included, pass line pre-registered).

Visual explainers (open in a browser): `../revenue-forecast-strategy/10_KERNEL_EXPLAINED.html` (start here),
`11_FINAL_PLAN.html`, `12_DATA_AND_QUANT_PLAN.html`, `08_THESIS_MAP.html`. Long-form: `../revenue-forecast-strategy/07_MORNING_REPORT.md`
and `AGENT_BRIEF.md`.

*Research, not investment advice.*
