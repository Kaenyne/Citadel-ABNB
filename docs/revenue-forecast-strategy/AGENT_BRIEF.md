# AGENT BRIEF — ABNB revenue-forecast programme

**Version 1 · 11 Sep 2026 · applies to every agent (Claude Code, Codex, or human) working in this repo.**
Read all of it once. Then claim a work package in `WORKBOARD.md` and follow its spec in §5.
If anything here conflicts with a number in a note, the note written later wins; say so in your own note.

---

## 1. Mission, in one paragraph

We are pitching Airbnb (ABNB) at the 2026 Citadel Intercollegiate Stock Pitch Competition: a 2-page memo plus
a model, due **2 Oct 2026**; finals in NYC **22–24 Oct**; judged by Citadel investors on a 3–12 month view.
The next print (**5 Nov 2026**, Q3 results + Q4 guide) lands after finals, so the memo is judged on a forecast of
**the guide and what it is made of**, not on a realised number. The chain the pitch runs on:

```
booked GBV (printed) → kernel λ → revenue → ÷(1+cushion) → guide → gap vs vendor-stamped Street
                                                                  → consensus revision → multiple (+0.48 turns / pt of fwd growth) → price
```

RNPL (Reserve Now, Pay Later; ~21% of GBV, no cash at booking, higher cancellations) enters the chain three
times — it inflates booked GBV and nights, it leaks from the kernel before check-in, and it sets when the
comparisons get hard (US lap 3Q26, global lap 1Q27). It is both a **variable** in the model and an **alpha thesis** (F).

**Recommended direction (pending the team's decision, WP-H): short.** From $181.94 (4 Sep) to a $157 base
(exit multiples 13.5 / 16.5 / 18.5x), bear $140–152, bull $205–215 — because an 18x multiple is paying for a
re-acceleration that the booking ledger says is largely arithmetic and decelerating. A written flip rule
(§4) covers the bull branch.

## 2. State of play — what is established (red-team confirmed, both PIT windows)

| Object | Number | Where |
|---|---|---|
| Kernel | revenue_q = λ_season × [⅔ GBV_{q−1} + ⅓ GBV_{q−2}]; λ Q1 12.66 / Q2 13.71 / Q3 17.24 / Q4 12.03 %; Q4 three-year range 0.17pp; reproduces to 2dp | `05_backtests/kernel-lambda.md`, `K1_*.md` |
| What the ⅔/⅓ means | measured split of the *pre-booked* part ≈ 70/30 (K2); ⅔ is also the PIT-optimal weight (0.65–0.70); the split is not identifiable from the ledger alone (φ₁+φ₂ = 0.58–0.64) | `K1_*`, `K2_*` |
| In-quarter share | φ₀ 0.36–0.39 (ledger) / 0.46–0.56 (booking data); say "~40% booked in-quarter", "most, not all, on the ledger" | `K1_*`, `K2_*` |
| Paid vs booked | next quarter's revenue at quarter start — Q3: 35% paid / 32% booked-unpaid / 33% not booked; Q4: 30 / 27 / 42 | `K1_*` |
| RNPL footprint | excess unpaid share of backlog +2.0 (4Q25) → +8.1 (1Q26) → +9.7pp (2Q26); u = 6–16%; leakage L 0.2–1.4% → −$8M to −$67M on 3Q26 | `K1_*`, `research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md` |
| λ control rule (5 Nov) | λ_Q3 = revenue ÷ $27,867M; < 17.09% (rev < $4,761M) warning; < 16.93% ($4,719M) escalate | `K1_*` |
| Once guided | guide × (1 + trailing-8 cushion) is the revenue forecast: RMSE ratio to naive 0.377 (W1) / 0.319 (W2); no single object beats it on both windows | `SCOREBOARD_v2.md` |
| Cushion | trailing-8 actual/guide mean +1.86%, median +1.79%, sd 1.006pp; 19/19 midpoint beats, 15/19 above the top | `guidance-policy.md` |
| 3Q26 revenue | ledger-only conditional $4,795M (80% $4,683–4,914); combined live $4,816M; guide $4,690–4,770M; Street $4,737–4,740M | `K1_*`, `B1_*` |
| 3Q26 GBV | ledger-only $26.4–26.6bn (80% $25.7–27.5bn); combined $26,549.8M (q10–q90 25,456–27,643); Krish's nowcast ≈ $25.9bn | `K1_*`, `B2_*`, `docs/q3nowcast/SYNTHESIS.md` |
| 3Q26 take rate | 18.14%, sd 0.46pp, P(≥ 18.10%) = 0.53 at GBV $26.55bn — **it is a GBV hinge**: 0.49 / 0.53 / 0.69 / 0.82 / 0.89 across GBV views | `B1_*`, `PREREG_ABNB-INT-v1.md` |
| Q4-26 guide (5 Nov) | midpoint $3,161M (80% $3,012–3,312) on own GBV; P(below) LSEG $3,158M 0.49 · S&P $3,160M 0.50 · Zacks $3,200M 0.63 (θ = 0.83 step: 0.43 / 0.44 / 0.57) | `B2_*` |
| FY27 | $15,838M / +11.52% at w = ⅔; band +9.18 to +11.52% across w; edge vs Street +0.09pp (−2.25pp at w 0.33); **exploratory**; GBV +11.51% invariant to w | `B3_*` |
| FX | revenue-FX effective lag 0.4–0.5 q in-sample (lag-2 weight ≈ 0); lag-loaded spec is the best PIT forecaster of stated FX; 4Q26 revenue FX +1.0pp (CS +0.3–2.2); the −3.4pp step double counts; pre-registered: stated 3Q26 FX ≈ +3 → kernel, 0/+1 → short lag | `B4_*`, `fx-lag.md` |
| Fees / θ | pass-through θ **unidentified** (the "0.83–1.41" was the detection window); uplift +1.1–1.8% at θ 0.83, +4.05% only at θ = 1; deadlines 15 Sep (non-EEA-resident hosts) / 13 Oct (EEA+CH), Resource Center art. 771, no year printed; only listed prices obtainable | `fee-takerate.md`, `A3_fee_panels.md` |
| Composition | geo mix −1.09 to −1.5pp and deepening; unit size +0.63pp (bedroom ε 0.23, not +2pp); LOS +0.04; seats −0.5pp; like-for-like price + sub-regional mix +2.8–3.6pp **unidentified** | `B3_*`, `research/notes/2026-09-07_adr-decomposition.md` |
| Consensus | Yahoo = Alpha Vantage = one LSEG-family panel; independent Q4 anchors LSEG ~$3,158–3,160M, S&P $3,160M, Zacks $3,200M (10 est.); the 6 Aug pre-guide Q3 Street is LSEG $4,610M, not Zacks $4,740M | `A1_consensus_vintages.md`, `L0_vintage_register.csv` |
| Valuation | multiple moves +0.48 EV/EBITDA turns per pt of forward revenue growth, margin 0; fair exit 13.5 / 16.5 / 18.5x; football field base $154–157 vs spot $182 | `docs/overnight/FINAL_SUMMARY.md` |
| Nights (Krish / Theo) | reviews stays index beats naive (0.68): 3Q26 +9.5–10.0%; team baseline +9.9%; Theo's RNPL re-base +9.3% (band 8.8–9.8), 4Q26 +7.6% (7.2–8.1) vs 8.9%; ex-NA lap question 8.0–8.2% | `docs/q3nowcast/SYNTHESIS.md`, `docs/overnight2/SYNTHESIS.md`, `data/processed/nights_baseline_reconciliation.csv` |

What is **not** established: any level edge on a guided quarter; a two-quarter FX lag (rejected in-sample);
a measured θ; a measured like-for-like price; a current Airbnb booking-lead-time distribution; whether unearned
fees or funds payable carries the FX confound (K1 vs Theo's note disagree — WP-F resolves it).

## 3. The eleven open team decisions (from `PREREG_ABNB-INT-v1.md`)

D-01 guide+cushion $4,816M vs kernel $4,804M as the 3Q26 revenue card value · D-02 reviews index vs team baseline
for nights · D-03 ADR card v2 quoted with its FAIL · D-04 which 3Q26 **block** to register (block ii: 147.38M /
$180.15 / $26,550M recommended; the object-by-object hybrid breaks the identity by −3.1pp) · D-05 lag-loaded FX →
predict ≈ +3 for stated 3Q26 FX · D-06 which balance-sheet line is FX-clean · D-07 no-fee-step Q4 guide as
headline · D-08 adopt the ex-NA lap (Q4 nights 8.0–8.2%) · D-09 predictive sd (3.03% conditional) · D-10 the
funds-payable refutation condition (written two incompatible ways: < +3% vs ≥ +11%) · D-11 the 4Q26 ex-NA lap
chained with PR #32's 1Q27 lap double-counts ~0.8pp. **Agents do not make these calls; they lay out the options.**

## 4. The pitch skeleton (so every package knows what it feeds)

1. **Mechanism.** Revenue is converted, not forecast: ~60% of a quarter is booked before it starts, ~35% paid; λ moves
   0.17pp; the guide is arithmetic over a shrinking cushion; 19/19 beats are mechanics.
2. **Composition (the variant view).** FY26→FY27 halving = dollar lap (an output of the kernel, not a −3.4pp
   subtraction) + product-bundle lap (RNPL + cancellation redesign + total price) + mix identity. Both narratives
   on the tape misread the shape.
3. **The trade and the flip rule.** Short, target $157; the 5 Nov guide is a coin toss vs the broad panels, below
   vs Zacks; the asymmetry is the 3Q26 take rate *read together with GBV*. **Flip:** cover and go long if take rate
   ≥ 18.10% on GBV ≥ $26.3bn AND Q4 nights guided "low double digit"; add if λ_Q3 < 16.93% or nights "high single digit".
4. **RNPL is the bear engine.** Unpaid share +10 points, higher cancellations (2Q26 10-Q), laps in 3Q26 and 1Q27.

## 5. Work packages — specs

Every package: copy-never-overwrite; new folder `analysis/src/forecast_methods/<pkg>/` with `run.py` (exit 0) and
`README.md`; outputs `data/processed/forecast_methods/<pkg>/`; registry files only under a new method name;
note `docs/revenue-forecast-strategy/05_backtests/<WP>_<slug>.md` with the template in §7; then `harness/score.py`.

### WP-A · Thesis A — guide surprise (Krish lane · 1 agent-day · data on disk)
**Claim.** The kernel-implied guide forecasts the actual guide (sd ≈ 1.1pp) better than the Street's expectation (sd ≈ 2.5pp); when they disagree by > 1pp the sign of the guide surprise is forecastable.
**Signal.** At each guide date d (14 on W1; extend to 19–23 with older, flagged consensus): `S = kernel_guide(q+1) − consensus(q+1)` in %, where kernel_guide = c_s(PIT) × [⅔ GBV_q(just printed) + ⅓ GBV_{q−1}] ÷ (1 + c_d trailing-8 PIT cushion), and consensus is the latest vintage strictly before d from `L0_vintage_register.csv` / `16_consensus_at_print_merged.csv` (vendor column kept; never a September value for a historical date).
**Targets.** (i) sign and size of `actual_guide_mid − consensus`; (ii) executable next-open returns at 1, 5, 20 days (`abnb_earnings_reactions.csv`, `open_*` columns only), conditional on sign(S) and on |S| > 1pp.
**Baselines.** zero; sign of the previous guide surprise; guide+cushion computed on consensus instead of GBV.
**Pass line (pre-registered).** Sign hit-rate ≥ 70% on |S| > 1pp cells on BOTH windows, AND the conditional 20-day mean return has the predicted sign on both windows. Report the count of |S| > 1pp cells; if < 6, say the test is underpowered and publish anyway.
**Outputs.** `alpha_a/`: per-date table (S, actual gap, vendor, returns), hit-rate tables, a figure; register `alpha-a__guide_gap_next_q` (PIT) and the live 5 Nov row; note `ALPHA_A_GUIDE_SURPRISE.md` with the "may the memo claim an expectations edge?" verdict in the first paragraph.

### WP-F · RNPL as a variable and as a thesis (Theo lane · 1–2 agent-days + Theo review)
**Objective.** Put RNPL into the model explicitly and pre-register its tells; resolve the FX-confound disagreement.
**Do.** (1) Rebuild the paid backlog (unearned fees + funds payable) and its seasonal coverage norms; (2) re-derive u (unpaid share) and m (migration share) by the joint solve, publishing the range and the excess-unpaid series; (3) resolve D-06 by reading the FY2025 10-K and 2Q26 10-Q notes on which line is translated at historical vs period-end rates and which is affected by the host-only fee (write the reasoning and the quote); (4) implement `rnpl_v2/`: revenue_q = c_s Σ φ_k GBV_{q−k} (1 − L_q) with L from `overnight2/D/D1_rnpl_cohort_scenarios.csv` × RNPL share; λ control chart with bands and the 5 Nov thresholds; the re-based nights bridge as a switchable input (team baseline / Theo re-base / ex-NA lap); (5) write the F thesis: setup (reported GBV/nights ran ~4 points ahead of the paid backlog from 3Q25; multiple 13.3x → 18.2x), the tells (λ, funds payable y/y +5–11% = on schedule, cancellation language, bundle figure restated, Q4 nights word), and the refutation condition — one version, replacing D-10's two.
**Pass line.** The excess-unpaid series reproduces (+2.0 / +8.1 / +9.7pp); the λ chart's historical false-alarm rate is published; the model runs with each nights input and reports 3Q26 / 4Q26 revenue under each; D-06 has a documented answer.
**Outputs.** `rnpl_v2/`; register `rnpl-v2__revenue_next_q` (three nights variants, PIT where possible); `ALPHA_F_RNPL.md`; proposed card rows F1–F4.

### WP-E1 · Thesis E — NCLH advance-ticket-sales kernel (Jessie lane · 3–5 agent-days · free data)
**Objective.** Show the recognition kernel is a method: cruise lines book far ahead and disclose advance ticket sales (ATS).
**Do.** Pull NCLH quarterly balance sheet (ATS), income statement (passenger ticket revenue, onboard revenue) and KPIs (capacity days, occupancy, net yield) 2015–2Q26 via Alpha Vantage (`BALANCE_SHEET`, `INCOME_STATEMENT`, `EARNINGS`) and 10-Q text; build revenue_q = c_s Σ φ_k ATS_{q−k} (and the guide history from press releases); estimate λ by season ex-COVID (2020–21 excluded, 2022 flagged), its within-season range, the PIT walk-forward vs naive/AR(1)/guide+cushion; compute the guide-surprise hit-rate as in WP-A with whatever consensus history exists (Alpha Vantage `EARNINGS_ESTIMATES` history if available; otherwise press quotes, flagged).
**Pass line.** λ within-season range < 0.5pp over 2023–25 AND walk-forward ratio to naive < 0.6 on both windows; guide hit-rate ≥ 65% if consensus exists. Publish the negative if not.
**Outputs.** `alpha_e_nclh/`; `ALPHA_E_NCLH.md` with a one-page "does the method transfer?" verdict and the one figure (λ by season, ABNB vs NCLH).

### WP-B · Thesis B — term structure vs FY consensus (Krish lane · 2 days · after WP-A; better after WP-G1)
**Signal.** At each print date: `T = kernel_FY − FY_consensus`, kernel_FY = printed quarters + kernel(q+1) + kernel(q+2) + seasonal naive beyond; consensus from the vintage register (thin before 2024 — flag).
**Targets.** 30/60/90-day FY consensus revision; realised FY; 20/60-day executable returns.
**Pass line.** T predicts the sign of the 60-day revision ≥ 70% on dates with |T| > 0.5%; corr(T, revision) > 0.4 on both windows.
**Outputs.** `alpha_b/`; `ALPHA_B_TERM_STRUCTURE.md`.

### WP-C1 · Calendar pickup ≤ 90 days → booked-GBV feature (Theo lane · after the September dumps)
**Objective.** The first alt-data object aimed at booked GBV instead of nights.
**Do.** For consecutive monthly Inside Airbnb calendar dumps (2024–25 vintages: 34 markets under `data/raw/inside_airbnb_calendar/`; 2026: `~/abnb_ia_capture/`), for the same listing and stay date, count nights that flip available → unavailable between dumps, restricted to stay dates ≤ 90 days ahead of the later dump (K2: beyond ~90 days blocked ≠ booked). Aggregate by market and month; weight by listing price where the dump carries one (2024–May 2025 only) else by nights; build a y/y pickup index; calibrate cross-sectionally to disclosed GBV y/y on the 13 quote cities; test PIT on W2.
**Pass line.** Right-signed correlation with disclosed GBV y/y on the available vintages and beats the RNPL-corrected unearned-fees baseline on W2 (W1 not available). Publish the negative if not.
**Outputs.** `pickup_v1/`; register `pickup-v1__gbv_yoy_current_q`; `ALPHA_C1_PICKUP.md`.

### WP-C2 · Macro / arrivals pulls (Theo lane · 1 day)
Extend `analysis/src/q3nowcast/G/` into one script `macro_pulls/run.py`: NTTO I-94 monthly arrivals by country; Eurostat platform nights monthly; JNTO, INE Frontur/Egatur, DATATUR, ISTAT monthly; STR/CoStar weekly US RevPAR and ADR (press releases); CPI lodging (FRED). Manifest with SHA-256 and pull date; no scraping of anything behind a login. **Pass line:** every series has a documented URL, cadence and publication lag; the NTTO series reproduces the survivor result (0.72–0.74x on nights).

### WP-C3 · Retarget the alt-data features at booked GBV and at R (Krish lane · after WP-C1)
Re-point the 598-feature machinery (`analysis/src/overnight/08_altdata_backtests.py`) at (a) booking-dated GBV y/y and (b) the kernel residual R_q from `kernel_phi_v2/`; PIT; both windows; pre-register the feature list before running. **Pass line:** a feature earns a place only if it beats the ledger baseline on GBV on both windows with a stable sign.

### WP-D · λ chart and backlog split into the card (Krish lane · hours)
Add to the card: λ_Q3 thresholds; the paid/unpaid/not-booked split; the excess-unpaid series; the funds-payable score line (after WP-F resolves D-06/D-10). No modelling.

### WP-E2 · BKNG / EXPE deferred merchant bookings (Jessie lane · after E1)
Same as E1 on deferred merchant bookings. Optional; only if E1 transfers.

### WP-G1 · LSEG estimates history → vintage register (Theo lane · after WP-G0, human)
Once Theo has registered for LSEG Workspace and granted the browser extension site access: export estimates history (revenue by fiscal period, monthly statistics dates, 2021–today) for ABNB, NCLH, BKNG, EXPE; save under `data/raw/consensus/lseg/` (licensed — off git, manifest only); run `analysis/src/forecast_methods/L0/consensus_history_loader.py` (append-only, backup first). **Pass line:** the register gains vintage-stamped rows at every historical guide date; the 6 Aug 2026 Q3 value matches LSEG $4,610M.

### WP-H · Direction and target reconciliation (human · this weekend)
Inputs: `docs/overnight/FINAL_SUMMARY.md` (football field $154–157 base), `deck/drafts/memo_v0_2026-09-11.md` (branch analogues $170–185 / $140–152 / $205–215), `B3_*` (FY27 band), `docs/overnight2/SYNTHESIS.md` (ex-NA lap). Output: one line in the card — LONG / SHORT, target, three branch prices with probabilities — and `05_backtests/H_DIRECTION_DECISION.md` with the reasoning. An agent may prepare the side-by-side table; a human signs it.

### WP-I · Memo v1 (Writer · after WP-H · 17 Sep)
Direction committed; §4 structure; the B2 grid as the one chart, the B4 four-way as the one table; every number stamped (PIT / full-sample; vendor, date); kill list applied; two pages at 10.5pt. New file `deck/drafts/memo_v1.md`.

### WP-J · Re-score and verify (any lane · recurring)
After any registration: `harness/score.py`; write `SCOREBOARD_v3.md` (new file) if the leaders change; spot-recompute eight cells from the registry CSVs; flag empty-ratio rows as "no baseline", not "failed".

### WP-K · September Inside Airbnb batch (Theo lane · when it lands, mid/late Sep)
Confirm the daily capture fetched it (manifest); pull the unlisted Aug 2026 batch (86 markets) if still missing; refresh the reviews stays index (Krish's E) and the party-size series (I); hand WP-C1 its vintages.

### WP-L · Airbnb policy monitor (Theo lane · hours to set up, weekly after)
Fetch + diff ~10 URLs (Help Center articles 1857, 4095; Resource Center 771, 746; Newsroom RNPL and cancellation pages; the host fee page); log every change with date and quote to `data/manifests/policy_monitor.log`. Read-only, rate-limited, no login.

### WP-M · Consensus re-stamp (Theo lane · weekly; 2–3 Nov)
Alpha Vantage `EARNINGS_ESTIMATES` (via MCP in Claude; via API key elsewhere), Zacks page capture, S&P where visible; append to the register with vendor + timestamp; never overwrite. On 2–3 Nov Zacks posts nights / ADR / GBV consensus — capture it.

### WP-N · Fee panels and θ (Jessie lane · runs 14/16/18 Sep, 12/14/16 Oct)
Launchd job runs the capture. On 16 Sep measure panel overlap between runs (≥ 40% needed); after 18 Sep estimate θ by difference-in-differences on listed price, migrating cohort (non-EEA-resident hosts) vs EEA control, and report with a CI; state that the guest-side total is not measured. **Pass line:** overlap ≥ 40% and a θ CI narrower than 0.83–1.41.

### WP-O · Terms-of-service decisions (human)
Three items no agent may take: the fee-inclusive quote route (GraphQL); Experiences / Services / hotel listing counts from search pages; an AirDNA purchase (realised ADR and current lead time — the only source for two "unidentified" labels). Log the decision in `WORKBOARD.md`.

### WP-P · Card freeze and score sheet (Writer · 26 Sep; 6 Nov)
Freeze `PREREG_ABNB-INT-v1.md` after WP-H, WP-F and WP-A; on 6 Nov score every item against the print with the rules written in the card.

## 6. Kill list — never quote these as ours

The −3.4pp Q4 FX step (double subtraction) · "82% of Q4 FX already determined" · "+4.05% fee uplift" as measured ·
the 9/9 guide-below-Street drift rule as a tradeable signal · "half of ADR growth is bigger units" (it is +0.46–0.8pp) ·
any FY27 level edge without the +9.2–11.5% band · any p-value for the drift rule · restated unearned fees
(`reported / (1 − d)`) as a pin or a feature (circular) · the 1.71M quote panel as "fee-inclusive" (it is not) ·
"nothing beats guide × cushion" (say: no single object beats it on both windows) · mixing a September consensus
value into a historical guide date · M5's hierarchical cushion model · the 120-market panel as a nights measurement ·
the Stan state space for the prelim. Full lists: `05_backtests/RED_TEAM.md`, `research/notes/overnight/14_master-synthesis.md` §11.

## 7. Note template (copy this into `05_backtests/<WP>_<slug>.md`)

```
# <WP> — <title>
Agent/session · date · branch · packages touched (all new) · time spent
## Verdict (first paragraph, plain language): pass / fail / partial against the pre-registered line
## What ran: exact commands; exit codes; wall time
## Results: tables with n on every row; PIT vs full-sample labelled; vendor + timestamp on every consensus number
## What failed or could not be done, and why
## Interpretation (honest; no number from §6)
## Harness change requests (if any)
## RESUME: what the next agent should do, in one paragraph
```

## 8. Working in parallel without collisions

- One package per agent; claim it in `WORKBOARD.md` first. Never edit another package's folder or note.
- Registry: your files only, under your method name; the scorer handles the rest.
- Shared inputs (KPI panel, L0 files, harness) are read-only for everyone. If L0's vintage register needs rows,
  back it up as `L0_vintage_register.backup_<date>.csv` first and append only.
- Git: your own branch `<name>/<wp>`; PR to `main`; never rebase someone else's branch. Large outputs (> 50 MB)
  and licensed exports stay out of git; commit the manifest.
- If you find an error in an earlier note, do not edit it — write a dated correction in your own note and add
  one line to `WORKBOARD.md` under "Corrections".

## 9. Where things are

**Contributor kit for this thesis:** `docs/thesis-kernel-topdown/` — README (thesis in six sentences, package table),
`01_CONTEXT.md`, `02_SETUP.md` (clone, venv, smoke tests), `03_NUMBERS_CHEATSHEET.md`, `04_DATA_MAP.md`, and `prompts/`
with one paste-ready prompt per work package (WP-A, B, C1–C3, D, E1–E2, F, G1, J, L, M, N). Send a contributor the repo
link and the prompt file; nothing else is required.

`01_ground-truth/` (data inventory, model audit, insider mechanics, recent facts, alt-data landscape) ·
`02_proposals/` and `03_critiques/` (the six methods and their red teams) · `04_synthesis/` (the architect's plan) ·
`05_backtests/` (every package note, verify notes, B1–B4, K1–K2, A1–A3, card, scoreboard, red team) ·
`07_MORNING_REPORT.md` · `08`–`12_*.html` (the visual explainers: thesis map, next-12-hours, kernel explained,
final plan, data & quant plan) · code `analysis/src/forecast_methods/` · data `data/processed/forecast_methods/` ·
captures `~/abnb_ia_capture/` (outside the repo) with manifests in `data/manifests/`.

## 10. Corrections log

- 11 Sep: the fee-deadline dates DO have a repo source (FEE-01 / art. 771) — an earlier runbook said they did not.
- 11 Sep: `06_quote_line_items.csv` is not fee-inclusive (service fee, cleaning fee, taxes null).
- 11 Sep: calendar "booking curves" (blocked rate by horizon) are U-shaped past ~90 days — they measure blocks, not bookings.
- 11 Sep: K1 reads unearned fees as FX-clean and funds payable as FX-confounded, the reverse of Theo's RNPL note — open (WP-F, D-06).
- 11 Sep (evening) — two deliberate exceptions to "copy, never overwrite", both code-only, no data or result changed:
  (a) portability: `kernel_leadtime_v2/K2_*` ROOT and `red_team/rt_*` REPO now derive from the file location (env override
  `CITADEL_ABNB_PARENT`), `red_team/run.py` uses `sys.executable`, and machine-specific interpreter paths in docstrings/READMEs became
  `python`; (b) `L0/test_l0.py`: two assertions updated to accept A1's 11 Sep register appends (S&P FY27 relay 15,770; QUARANTINED rows
  with a stated reason). Verified in a fresh shallow clone: harness 27/27, kernel acceptance PASS on 12 cells, scorer exit 0.
