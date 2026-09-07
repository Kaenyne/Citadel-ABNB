# Handoff: what changed in PR #16 (branch `krish/overnight-synthesis`)

Krish, 6-7 Sep 2026. Two minutes to read. Ask me before editing anything under `overnight/`.

## What this PR is

One branch that holds everything: origin/main, all seven open PRs (#5, #8, #11-#15), four branches I never pushed, and the overnight research run on top. Merging it closes those PRs. `data/README.md` and `research/sources/README.md` were tidied after the merge (S-numbers S30 to S37 that collided are remapped to S40+; see `data/processed/overnight/25_source_id_remap.csv`).

## The five things that matter

1. **We have a model now.** `model/ABNB_driver_model.xlsx` (9 sheets, live formulas, scenario selector on Inputs!B4) with a Python mirror that reconciles cell for cell. Base 12-month target $157 (bear $74, bull $228) vs $181.94 spot. Assumptions and sources in `model/assumptions.md`, section "Overnight run".
2. **The old $248 base case was the exit multiple, not the business.** Three independent methods put fair EV/EBITDA at 13.5/16.5/18.5x, not 18/22/25.5x. No published price target implies 22x. If we pitch a long, the upside has to be argued from FY27 revenue, SBC, or named optionality.
3. **Revenue FX lags spot by one to two quarters.** The Q4 2026 guide steps down about 3 points on arithmetic alone. Build that bridge before 5 Nov so nobody reads it as a demand break.
4. **Almost nothing predicts the print or the stock, and we can now say so with receipts.** About 3,500 tests. Survivors: dollar-to-ADR FX, guide plus cushion for revenue, and "guide below Street" (9 of 9 negative over 20 days, small). Alt data, Google Trends, macro, tone, peers: nothing beats a naive baseline on both windows.
5. **Everything was audited twice.** A red-team pass (98 claims) and an independent audit (13 findings, all closed in commit 55c9b49). Withdrawn claims are listed in `research/notes/overnight/14_master-synthesis.md` section 11.

## Where to look

| Want | Open |
|---|---|
| The two-page version | `docs/overnight/FINAL_SUMMARY.md` |
| Full synthesis, 5 Nov prediction card, pitch implications | `research/notes/overnight/14_master-synthesis.md` |
| One topic in depth | `research/notes/overnight/01_` to `26_` (data census, KPIs and guidance, management language, consensus, macro, consumer choice, margins, alt data, stock behaviour, regions, competition, valuation, model, synthesis, red team, follow-ups, audit repairs) |
| Rebuild anything | `docs/overnight/BUILD.md` (`py -3.13`, Excel needed for the workbook audit) |
| What each number came from | `data/processed/overnight/26_change_ledger.csv` and `15_claim_checks.csv` |

## Before 5 Nov

Refresh `data/processed/overnight/05_fx_schedule.csv` weekly (one FRED pull). Pull the Zacks nights/ADR/GBV consensus 2-3 days before the print. Score the frozen card in `20_frozen_q3_2026.csv` on 6 Nov. Start the monthly Inside Airbnb capture; their CDN keeps about a year.

## Housekeeping after merge

Close PRs #5, #8, #11-#15. Delete the branches they came from and the nine `citadel-abnb-*` worktrees next to the repo. The main checkout still has an old uncommitted copy of the regulatory work; it is superseded by what is in this PR.
