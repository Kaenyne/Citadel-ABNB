# Citadel-ABNB repo: state of play, 7 Sep 2026

Compiled by Krishang with Claude Code from `git fetch`, `gh pr list`, `git worktree list`, the zip contents on `origin/main`, and the 6 Sep inventory (`docs/2026-09-06_research-inventory.md`, which has the number-level detail this note only points at).

## 1. Headline

- **One PR holds almost everything.** PR #16 (`krish/overnight-synthesis`, 448 files, +308k lines) union-merges the seven other open PRs, four unpushed branches, and the 6-7 Sep overnight research run. Merging it closes #5, #8, #11-#15.
- **PR #16 no longer merges cleanly.** Since it was opened, Jessie's PR #17 and thirteen zip uploads landed on `origin/main`. A dry merge conflicts in three files: `data/README.md`, `requirements.txt`, `research/sources/README.md`. All three are catalogue files, so the fix is a short rebase.
- **The repo is 41 MB over 579 files on `origin/main`, plus 520 MB of worktrees on disk.** The bulk is Theo's Codex archive (`theos-past-research/`, about 330 files) and 14 zip files at the repo root that were uploaded through the GitHub web UI and never unpacked.
- **Local `main` is 20 commits behind origin** with 92 untracked or modified files (regulatory package, `ABNB-Crossover/`, older driver-model outputs). Everything in it that matters is superseded by PR #16.

## 2. Open branches, PRs and worktrees

| PR | Branch | Worktree | What it is | Status |
|---|---|---|---|---|
| #16 | `krish/overnight-synthesis` | `../citadel-abnb-overnight` | Everything below plus the overnight run, the Excel driver model, red team and audit | Open, 3 conflicts vs main |
| #15 | `krish/regulatory-forecast` | `../citadel-abnb-reg` | 20-event regulatory Monte Carlo on the 32-factor register | Open, in #16 |
| #14 | `krish/eu-platform-backlog` | `../citadel-abnb-eu` | Eurostat platform-nights benchmark, XBRL backlog indicators | Open, in #16 |
| #13 | `krish/driver-model` | `../citadel-abnb-model` | 5 Sep Python driver model ($176/$248/$325); superseded by the Excel model | Open, in #16 |
| #12 | `krish/cc-listing-panel` | `../citadel-abnb-cc` | Common Crawl matched-listing panel 2021-2026 | Open, in #16 |
| #11 | `krish/inside-airbnb-supply` | `../citadel-abnb-supply` | Inside Airbnb supply panel, 13 cities, 168 dumps | Open, in #16 |
| #8 | `krish/margin-drivers` | `../citadel-abnb-margin-gaps` | XBRL cost lines, margin bridge, FCF bridge, BKNG head-to-head | Open, in #16 |
| #5 | `krish/plan-of-attack` | none | 5 Sep plan through the Q3 print | Open, in #16 |
| none | `krish/capital-return-panel` | `../citadel-abnb-margin` | Buyback and SBC panel, 7-name peer scorecard | Local only, in #16 |
| none | `krish/predictive-study` | `../citadel-abnb-predict` | Base rates, peer read-through, macro nowcasts, pitch scorecard | Local only, in #16 |
| none | `krish/transcript-analytics` | `../citadel-abnb-transcripts` | Call roster, topic mix, "declined to quantify" ledger | Local only, in #16 |
| none | `krish/guidance-margin-items` | none | 44 margin guides added to Theo's guidance dataset | Local only, in #16 |

Merged and closed: #1 (Theo's Codex import), #2-#4 and #6-#7 (pitch catalogue, management timeline, Third Bridge digest, major moves, pitch landscape), #9-#10 (Theo's alt-data acquisition layer and booking curves), #17 (Jessie's consolidated alt-data workstream). Remote branches `theo/alt-data-acquisition` and `codex/theos-past-research-import` are fully merged and can be deleted.

## 3. What is on `origin/main` today

**Krish's research notes** (`research/notes/`): pitch catalogue and landscape, management timeline, major stock moves with earnings-reaction tables, the 22-quarter earnings-call study, the Third Bridge digest.

**Theo's work**: the alt-data acquisition layer (`analysis/src/acquisition/`), booking-curve aggregates from 588M calendar rows across 120 markets, the 2026 market summary, and the full Codex archive under `theos-past-research/` (alt-data controls, macro-to-guidance forecasting packets, guidance contracts, 37 tests). The archive is a historical snapshot, not live research.

**Jessie's work** (PR #17 plus zips): air-traffic and macro top-down studies, Austin daily STR licences, Airbnb-vs-hotel choice data, Eurostat crowding tests, Hawaii DBEDT accommodation splits, NYC OSE enforcement, Vancouver licences. The zip drops hold work not yet in the tree: direct-booking leakage, catalyst calendar with 7%+ move stats, host-only fee-split elasticity model, hotel loyalty stickiness, hotel news impact, revenue-model comparison vs BKNG/EXPE, and six versions of a stay-length and party-size study whose latest (v6) adds a choice-driver projection model.

**Scaffolding**: `model/assumptions.md`, `deck/` (empty drafts and final), `docs/competition/citadel_2026_format.md`, `docs/TIMELINE.md`, PR and issue templates.

## 4. Exploration projects, by theme

- **Supply side**: Inside Airbnb panel (like-for-like price, churn, host concentration, 1.71M fee-inclusive quotes), Common Crawl survival and professionalisation panel, Theo's booking curves, Jessie's Austin licences.
- **Demand and macro**: Eurostat platform nights, BEA PCE travel, FRED, TSA/IATA/BTS air traffic, Google Trends, NTTO inbound, peer prints for BKNG/EXPE/MAR/HLT.
- **Regulatory**: 32-factor register, 48 sources, SQLite full-text database, identifier-matched cohorts (Barcelona, Maui), Hawaii vintages, Monte Carlo.
- **Company and Street**: 119-column KPI panel 1Q21-2Q26, guidance ledger (194 statements), consensus reconstructed at all 23 prints from press quotes, 466 sell-side actions, monthly point-in-time multiples, options ledger.
- **Language**: 23 transcripts and letters parsed, 1,677 speaker turns, 83 management claims scored for credibility.
- **Consumer choice** (Jessie): stay length, party size, kitchen and whole-home premium, hotel loyalty, direct-booking leakage.
- **Predictive tests**: about 3,500 tests across reaction function, nowcasts, alt data and valuation. Five survivors, all small; nothing beats a naive baseline for the print or the stock.

## 5. Models

| Model | Where | State |
|---|---|---|
| Excel driver model, 9 sheets, 2,353 formulas, scenario selector | `model/ABNB_driver_model.xlsx` on #16, Python mirror `13_driver_model.py` | Verified in Excel, 0 errors. Bear $74 / base $157 / bull $228 vs $182 spot |
| 5 Sep Python driver model | PR #13 | Superseded; exit multiples 18/22/25.5x not supportable |
| Margin lever model, 40k-draw Monte Carlo | PR #8, overnight WS07 | Live |
| Regulatory Monte Carlo, 200k draws, Gaussian copula | PR #15, repaired on #16 | Live |
| Fee-split elasticity, choice-driver projection | Jessie's zips | Exists only inside zips |
| Reaction function, nowcast, valuation harnesses | Predictive branch and overnight WS02-WS12 | Negative results, documented |

Standing instruction: operating views (revenue, margin, EPS) come first; the valuation lenses and target prices are parked until those are agreed.

## 6. Housekeeping to shrink and simplify

1. Rebase `krish/overnight-synthesis` onto `origin/main`, resolve the three catalogue conflicts, merge #16, close #5, #8, #11-#15, delete their branches and the ten `citadel-abnb-*` worktrees.
2. Unpack Jessie's 14 root zips into `research/`, `data/processed/` and `analysis/src/` on one branch, keep only v6 of stay-length, then delete the zips from the tree. Ask contributors to open PRs instead of uploading zips.
3. Purge the five Third Bridge PDFs tracked under `research/` (licensed). They stay in history unless it is rewritten.
4. Decide whether `theos-past-research/` stays in the main repo or moves to its own archive repo; it is 60% of the file count and holds 10 MB of scrape CSVs.
5. Reset local `main` to origin after confirming the regulatory package and `ABNB-Crossover/` (a method-transfer kit from prior pitches, 784 KB, never committed) are either in #16 or intentionally dropped.
