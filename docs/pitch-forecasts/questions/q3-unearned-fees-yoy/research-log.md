# RESEARCH LOG

## 0. Metadata
- question_name: q3-unearned-fees-yoy
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § C12)
- type: binary
- run_mode: initial
- run_date: 2026-09-17
- open_date: 2026-09-17
- close_date: 2026-11-04
- resolution_date: 2026-11-05
- scoring: spot
- cp_visible: no
- cp_value: n/a
- revision: 1
- agent: fable

## 0b. Question (verbatim)
### Title
Will unearned fees on Airbnb's 30 Sep 2026 balance sheet be ≤ −3% year over year?
### Resolution Criteria
Yes if the 10-Q's unearned fees at 30 Sep 2026 divided by the 30 Sep 2025 figure, minus one, is ≤ −0.03. Resolution date: 3Q26 10-Q filing.
### Fine Print
Management's 1Q26 letter predicted higher unearned fees in Q3 from RNPL timing; the single-fee migration and FX confound the line (audit note 04). The log must decompose deferral, migration and FX before assigning probability.

Conventions adopted: (1) the 30 Sep 2025 base is $1,820M as printed in the 3Q25 10-Q balance sheet (the threshold is therefore ≤ $1,765.4M); if the 3Q26 10-Q restates the comparative, the restated comparative in the same 10-Q governs; (2) the 10-Q "Unearned fees" balance-sheet line in $ millions is the object, not the letter's rounded "$X.X billion"; (3) the 10-Q is expected the same day as the letter (the 2Q26 10-Q was filed 6 Aug 2026, accession 0001559720-26-000027); if later, resolution moves with it; (4) management's D038 sentence ("lower unearned fees in Q1 and Q2 and higher unearned fees in Q3") is read in this log as a statement about the *change* in the line during Q3 (deferred summer payments landing before check-in), not as a prediction that the 30 Sep stock is higher y/y; the D-note's level reading is carried as a hypothesis, not as the convention.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Unearned fees by quarter-end ($M): 1Q23 2,172; 2Q23 2,347; 3Q23 1,467; 4Q23 1,427; 1Q24 2,434; 2Q24 2,621; 3Q24 1,657; 4Q24 1,616; 1Q25 2,723; 2Q25 2,857; 3Q25 1,820; 4Q25 1,743; 1Q26 2,733; 2Q26 2,831. Y/y: 3Q25 +9.8%, 4Q25 +7.9%, 1Q26 +0.4%, 2Q26 −0.9%. GBV y/y: 13.9, 15.9, 19.2, 15.7. Gap (UF y/y − GBV y/y): −4.1, −8.1, −18.8, −16.7 points | `data/processed/overnight/02_kpi_panel_quarterly.csv` (unearned_fees_musd); `data/processed/abnb_backlog_indicators.csv`; `datasets/c12_history.csv` | 2026-08-06 (last print) | 2026-09-17 | yes |
| 2 | Q3 sequential change in unearned fees (30 Jun → 30 Sep): 2023 −37.5%, 2024 −36.8%, 2025 −36.3% (mean −36.9%, sd 0.6pp); 2026 sequential changes have run weaker than 2025's each quarter: Q1 +56.8% vs +68.5% (2025) / +70.6% (2024); Q2 +3.6% vs +4.9% / +7.7%. Applying the 2023–25 mean Q3 change to 2Q26's $2,831M gives $1,786M (−1.9% y/y); each additional point of decline is −$28M (−1.6pt of y/y) | `datasets/c12_history.csv` (seq_pct) | 2026-08-06 | 2026-09-17 | yes |
| 3 | Unearned fees over next-quarter revenue, 3Q: 2023 0.661, 2024 0.668, 2025 0.655 (RNPL US launch quarter); 2Q: 0.691 / 0.702 / 0.698 pre-RNPL; 1Q26 0.757 vs 0.880 (2025), a −14% shortfall; 2Q26 at a 3Q26 revenue of ~$4,780M ≈ 0.592 vs 0.698, −15% | `data/processed/forecast_methods/tracker_backlog/01_backlog_rebuild.csv`; `datasets/c12_history.csv` | 2026-09-11 | 2026-09-17 | yes |
| 4 | FY2025 10-K Note 2, verbatim: "Host and guest fees are recorded as cash with a corresponding amount in unearned fees"; "For all bookings, the guest pays the booking amount to the Company, which disburses the booking amount to the host after check-in, net of the host's service fees"; "The full value of the service fees is recorded as cash and cash equivalents and unearned fees on the consolidated balance sheets upon receipt of the first installment payment"; seasonality: "During the third quarter, GBV is typically lower and check-ins reach their peak, resulting in decreased unearned fees." (D055) | `data/raw/filings/abnb_10k_FY2025.htm` | 2026-02-12 | 2026-09-17 | yes |
| 5 | Audit note 04 (verification of the RNPL balance-sheet note): the single-fee migration moves unearned fees *up* 3–4% per migrated booking (host-only fee 15.5% of the host price sits in unearned fees exactly as the split fees did), not down; the 4Q25 UF/FP divergence is FX translation of non-USD funds payable (+$627M in FY25), while unearned fees reconciles to the cash-flow statement within $3–8M (FY25 +5, 1H25 +5, 1H26 +3) and is therefore "the FX-clean, migration-neutral line"; solved on unearned fees alone, the unpaid RNPL share u is 13.9–15.4% at B 1.00 (median 13.0% at 1Q26, 15.1% at 2Q26) and 21.7–23.1% at B 1.10; "Krish's −3% row is not trippable by migration"; deferral-only table (m = 0): u 5% → +9.9%, 10% → +4.1%, 15% → −1.7%, 20% → −7.5%; "the line reaches −3% only at u ≈ 16%"; corrected 5 Nov rule scores (UF y/y − GBV y/y) with −18pts mapping to −3% at mid-teens GBV | `docs/rnpl-short-audit/04_balance-sheet-verification.md` §1, C2–C4; `data/processed/rnpl_short_audit/verify_bs_3q26_deferral_only.csv` | 2026-09-11 | 2026-09-17 | yes |
| 6 | The superseded note's deferral-only scenarios (with its refuted migration term) gave 3Q26 unearned fees from −2.1% (u 7, m 9) to −16.6% (u 12, m 18) and +7.5% with no migration; its pre-RNPL, pre-migration expectation at 4Q26 revenue $3,166M was $2,105M (+15.6%); the audit reproduces that expectation exactly | `research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md` §2.3 and STATUS header | 2026-09-11 | 2026-09-17 | no |
| 7 | 1Q26 letter, verbatim (D038): "Specifically, Reserve Now, Pay Later shifts the timing of guest payments closer to the date of stay, resulting in lower unearned fees in Q1 and Q2 and higher unearned fees in Q3." Same letter (D037): "Absent the impact of Reserve Now, Pay Later bookings … we expect that unearned fees and FCF would have grown year-over-year." 2Q26 letter (D051): "we held $2.8 billion of unearned fees as of June 30, 2026, which was relatively stable compared to June 30, 2025. Absent the impact of Reserve Now, Pay Later bookings, which defer guest payments from the time of booking closer to the date of stay, we expect that unearned fees would have grown year-over-year." | `data/raw/letters/1Q26_d23351dex991.htm`, `2Q26_d70413dex991.htm`; `data/processed/overnight2/D/rnpl_statement_ledger.csv` D037, D038, D051 | 2026-05-07 / 2026-08-06 | 2026-09-17 | yes |
| 8 | 2Q26 10-Q MD&A (D057, D058), verbatim: "Unearned fees typically rise when GBV rises since guests pay at the time of booking … However, increasing adoption of RNPL, which shifts payment and unearned fees closer to the date of stay, is changing the typical seasonal dynamics between GBV and FCF"; "under our RNPL option, payment is collected closer to check-in rather than at booking. Accordingly, unearned fees are not recorded, and operating cash flows are not generated until payment is received." Six-month cash-flow line "Unearned fees" 1,085 (2026) vs 1,236 (2025) | `data/raw/regulatory/quantification/abnb_2026q2_10q.html` | 2026-08-06 | 2026-09-17 | yes |
| 9 | RNPL adoption path: US launch Aug 2025 (3Q25 letter); international expansion Feb 2026 (4Q25 letter; TechCrunch 2026-02-17); "roughly 20% of global GBV" in 1Q26 (1Q26 letter); "over 20%" 2Q26 (call mirror); "in July, we expanded the types of bookings eligible for Reserve Now, Pay Later" (D044, 2Q26 call, size not given); lead times lengthened in all regions (1Q26 letter) | `data/raw/letters/3Q25_…`, `4Q25_…`, `1Q26_…`; `data/raw/transcripts/web/2Q26.html`; ledger D044 | 2025-11-06 to 2026-08-06 | 2026-09-17 | yes |
| 10 | Pre-registered threshold row (D1): 3Q26 quarter-end unearned fees y/y "at or below −3% (below about $1,765mm)" supports the drag; "at or above +6% (about $1,930mm or more)" weakens it; −3% to +6% inconclusive; identifies "payment timing, not cancellation" | `data/processed/overnight2/D/D1_prereg_thresholds.csv` row 2; `research/notes/overnight2/D_rnpl-statement-ledger-and-cohort-scenarios.md` §5 | 2026-09-11 | 2026-09-17 | yes |
| 11 | Team 3Q26 GBV ≈ $25.9bn (+13.2%; nights +9.5%, ADR +3.3%); Street/MODL $26,375M (+15.2%); Kalshi-implied ≈ $26.26bn; bridge v3 4Q26 revenue $3,178M (v2 $3,135M); 3Q26 revenue ≈ $4,780M at the guide midpoint plus the Q3 cushion | `docs/q3nowcast/SYNTHESIS.md`; `data/processed/reverse_dcf/E/E_street_distribution_vs_team.csv`; `data/processed/h2_bridge_v3/h2_bridge_revenue_dollars.csv`; `../q3-take-rate-above-1810/research-log.md` claims 8–9 | 2026-09-11 to 2026-09-17 | 2026-09-17 | yes |
| 12 | Fee mechanics: split fee = guest ~14.1% + host 3% (≈ 14.99% of the guest total); single fee 15.5% of the host price; per booking the fee held in unearned fees rises +1.8% (θ 0.83) to +4% (payout-neutral); GBV-weighted migrated share (fee-takerate table) 0.24 (1Q26), 0.47 (2Q26), 0.70 (3Q26), 0.96 (4Q26); tranche-2 deadlines 15 Sep (non-EEA) and 13 Oct (EEA/CH) — third-party confirmation smoobu 2026-07-09 | `05_backtests/fee-takerate.md` §1–2; https://www.smoobu.com/en/blog/airbnb-host-only-fee-increase/ | 2026-09-11 / 2026-07-09 | 2026-09-17 | yes |
| 13 | RNPL help page: "your payment method will be charged on the scheduled date listed at checkout"; "available only for listings with certain cancellation policies"; no days-before-check-in figure published — the unpaid share at a quarter end therefore cannot be pinned from public terms | https://www.airbnb.com/help/article/2143 | unknown (no page date) | 2026-09-17 | no |
| 14 | Monte Carlo (this log, `datasets/c12_model.py`): Route A (y/y gap: UF y/y = GBV y/y − k·(u_3Q26 − u_3Q25) + migration + FX; GBV N(13.2, 1.9), u_3Q26 N(18, 3), u_3Q25 N(3.5, 1), k N(1.16, 0.15), migration N(+1.0, 0.7), FX N(0, 0.5)): P(≤ −3%) 0.455, median −2.5%; Route B (sequential: 2Q26 × (1 + N(−36.9, 0.6) + deepening N(−1.5, 1.5))): 0.681, median −4.2%; Route C (level: 0.661 × 4Q26 revenue N(3,178, 60) × (1 − u) × (1 + migration 1.5%)): 0.594, median −4.0%; mixture 0.45/0.30/0.25: 0.558, median −3.6% ($1,755M), 10–90% −8.4% to +1.9%, P(≥ +6%) 0.015 | computed; `datasets/c12_routes.csv`, `c12_sensitivity.csv`, `c12_deferral_table.csv` | 2026-09-17 | 2026-09-17 | yes |
| 15 | Deferral table (k 1.16, u_3Q25 3.5, migration +1): at GBV +13.2% the line crosses −3% at u_3Q26 ≈ 18.3%; at +15.2% GBV at u ≈ 20%; at +11% at u ≈ 16.5% | `datasets/c12_deferral_table.csv` | 2026-09-17 | 2026-09-17 | yes |
| 16 | No market prices this line (Polymarket searches; Kalshi ABNB series are nights ladders); web pass (2 WebSearch calls attributable) found no third-party estimate of Q3 unearned fees; one host-industry page (upgradedpoints, undated) claims "70% adoption on eligible bookings" — not fetched, zero weight | `sources/web_queries_2026-09-17.md`; `../q3-take-rate-above-1810/sources/` | 2026-09-17 | 2026-09-17 | no |

## 2. Query Log
1. [repo] read `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md`, skill `SKILL.md`, `references/research-log-format.md`, `examples/example-research-log.md`, `questions/q4-revenue-guide-vs-street/research-log.md`
2. [repo] `research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md`; `docs/rnpl-short-audit/04_balance-sheet-verification.md`; `research/notes/overnight2/D_rnpl-statement-ledger-and-cohort-scenarios.md` (§1.10, §5 via grep)
3. [repo, pandas] `data/processed/overnight/02_kpi_panel_quarterly.csv` (unearned fees, funds held, GBV, revenue); `data/processed/abnb_backlog_indicators.csv`; `data/processed/forecast_methods/tracker_backlog/01_backlog_rebuild.csv`; `data/processed/overnight2/D/D1_prereg_thresholds.csv`; `data/processed/abnb_filing_kpis.csv` (2Q26 rows); listing of `data/processed/rnpl_balance_sheet/`, `data/processed/rnpl_short_audit/`
4. [repo, python] "unearned fees" sentences from `data/raw/filings/abnb_10k_FY2025.htm` and `data/raw/regulatory/quantification/abnb_2026q2_10q.html` (claims 4, 8); RNPL / unearned-fee sentences from the 3Q25–2Q26 letters and the 2Q26 call mirror (claims 7, 9); ledger rows D037, D038, D044, D051, D055–D059
5. [repo] `05_backtests/fee-takerate.md` §1–2 (fee per booking, migrated share path); `docs/q3nowcast/SYNTHESIS.md`; `data/processed/h2_bridge_v3/` (4Q26 revenue)
6. [Polymarket public-search] airbnb; Airbnb Q3; Airbnb take rate; Airbnb revenue (2026-09-17T03:10:10Z) — no market on unearned fees
7. [Kalshi API] KXABNB, KXABNBA open markets (2026-09-17T03:10:10Z) — nights ladders only
8. [WebSearch] Airbnb news (neutral recency pass, shared by the batch — nothing on RNPL cash timing)
9. [WebSearch] Airbnb Reserve Now Pay Later unearned fees cancellations September 2026 (result: launch/expansion coverage Aug 2025 and Feb 2026, host-industry explainers; no Q3 estimate)
10. [WebFetch] airbnb.com/help/article/2143 (payment-timing sentences; no days figure)
11. [WebFetch] smoobu.com/en/blog/airbnb-host-only-fee-increase/ (migration deadlines, published 2026-07-09)
12. [python] `datasets/c12_model.py` — history, three routes, mixture, sensitivities, deferral table
13. [WebSearch, final 72-hour neutral recency check = query 8, 2026-09-17: no new RNPL, payment-timing or cancellation item] — no change to the number

WebSearch calls used by this question: 2 of 5.

## 3. Leading Hypothesis Entities
Airbnb, Reserve Now Pay Later, unearned fees, 10-Q balance sheet, Ellie Mertz, single fee 15.5%, funds payable, July eligibility expansion

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Management's D038 "higher unearned fees in Q3" is a level prediction, so the 30 Sep stock rises y/y and the answer is NO | discarded as the reading; kept as a NO scenario (P(≥ 0%) ≈ 0.25 in the mixture) | An RNPL booking never puts a fee into unearned fees earlier than the same booking without RNPL, so RNPL cannot raise the 30 Sep stock above its counterfactual; it can only make the Q3 *change* less negative as deferred summer payments land (convention 4). The sentence sits in the FCF paragraph. Management's own 2Q26 language ("relatively stable … absent RNPL would have grown") is a level statement and was −0.9% |
| The single-fee migration drags the line down (the superseded note's −2% to −17% deferral-only scenarios) | discarded | 10-K accounting (claim 4) and audit note 04 (claim 5): the host-only fee is collected at booking and sits in unearned fees; migration lifts the line +1 to +2pp y/y at a 50–70% migrated share, carried as the migration term with the opposite sign to the superseded note |
| FX translation moves the line | discarded as material (N(0, 0.5%)) | the balance change reconciles to the cash-flow "Unearned fees" line within $3–8M for six half-year/annual periods (claim 5); the FX swing lives in funds payable |
| The unpaid share u is seasonal — higher at 30 Sep (off-season backlog, far-dated stays) than at 30 Jun (imminent summer) | kept inside u_3Q26 N(18, 3) and Route B's deepening term | plausible but unmeasured: the 3Q25 base carried only ~6 weeks of US-only RNPL, so the y/y comparison at 30 Sep 2026 carries almost the whole u (claim 15); pushes toward YES |
| The July eligibility expansion and international ramp lift u to ≥ 20% | kept: sensitivity rows (u 20 → 0.64 / 0.79 by route) | D044 gives no size; flow share "over 20%" with a book turning over implies u converging toward the flow share |
| Unpaid share flat at 2Q26's 15% | kept as the main NO path (u 15 → 0.20–0.27) | adoption growth slowed in Q2 (sequential deepening only 1.3pt) |
| 4Q26 revenue (Route C's scale) is $3,130M not $3,178M | inside Route C's sd; sensitivity 0.72 | bridge v2 vs v3 |
| GBV prints at the Street's +15.2% rather than the team's +13.2% | kept: Route A sensitivity 0.30 | GBV growth is the dominant non-RNPL driver of the line; the audit's corrected rule scores the gap (UF − GBV) for this reason |

## 5. Independent Estimates
- base_rate_estimate: 0.46 — Route A: the 1H26 y/y gap (−18.8, −16.7 points) carried forward through Δu (u_3Q26 18% vs u_3Q25 3.5%, k 1.16), migration +1.0, FX 0, GBV +13.2% → median −2.5%, P(≤ −3%) 0.455 (claim 14)
- decomposition_estimate: 0.59 — Route C: pre-RNPL 3Q norm 0.661 × 4Q26 revenue $3,178M = $2,101M counterfactual, × (1 − u 18%) × (1 + migration 1.5%) → median −4.0%, P 0.594; Route B (sequential with 2026-style deepening) gives 0.68 and is blended into the decomposition object at 0.30/0.25 of the mixture (0.63 combined)
- anchor_estimate: 0.45 — no market; the anchor is the programme's own published deferral-only table (audit note 04, claim 5): −1.7% at the 2Q26 solved u of 15% and −3% at u ≈ 16%, i.e. the pre-registered threshold sits about one quarter of adoption growth ahead of the last print
- anchor_value: 0.45 (audit note 04 deferral-only table, 2026-09-11, evaluated at u 15–16% with the 1H26 u trend of +2 points per quarter)
- final_estimate: 0.55 (credible interval 0.40–0.70)
- final_minus_anchor: +10 points. NOT_INDEPENDENTLY_DERIVED flag applies in part: the anchor is an internal table built on the same balance-sheet series as the three routes, so the four numbers are not independent draws; the +10 comes from two things the anchor table holds fixed — the July eligibility expansion and the international ramp (u 18 rather than 15–16) and the 3Q25 base carrying only six weeks of US RNPL (Δu, not u, drives the y/y)

## 6. Final Numbers
**Binary.** P(unearned fees at 30 Sep 2026 ≤ −3% y/y, i.e. ≤ $1,765M) = **0.55**, credible interval **0.40–0.70**.
Mixture (`datasets/c12_routes.csv`): 0.45 × Route A (0.455) + 0.30 × Route B (0.681) + 0.25 × Route C (0.594) = 0.558. Median print ≈ $1,755M (−3.6%); 10–90% $1,667–1,854M (−8.4% to +1.9%). P(≥ +6%, the D1 "weakens" threshold) ≈ 0.015; P(between −3% and +6%, inconclusive) ≈ 0.43.
Decomposition of the central path (y/y points, from the deferral table and Route A means): GBV growth +13.2; deferral −k·Δu = −1.16 × (18.0 − 3.5) = −16.8; migration +1.0; FX 0.0; total ≈ −2.6 (the Route A median); Routes B and C land 1.5 points lower because they carry the 2026 deepening and the seasonal u respectively.
Extreme-probability gate: not triggered.

## 7. Sensitivity
Rows from `datasets/c12_sensitivity.csv` (single-assumption reruns within a route; the mixture moves by roughly the route's weight times the change).
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| GBV y/y +13.2 (team) in Route A | Street +15.2: 0.30; +11.0: 0.64 |
| u_3Q26 18% | 15 (flat vs 2Q26): 0.20 (A) / 0.27 (C); 20: 0.64 (A) / 0.79 (C); 22: 0.80 (A) |
| u_3Q25 base 3.5% | 5%: 0.32 (A) |
| Migration +1.0 ± 0.7 (A) / +1.5 (C) | 0 (audit's migration-neutral reading): 0.54 (A) / 0.73 (C); +2: 0.37 (A) |
| k 1.16 | 1.0: 0.26 (A) |
| Route B deepening −1.5 ± 1.5 | 0 (Q3 decline equals the 2023–25 mean): 0.26; −3 (1Q26-style): 0.92 |
| 4Q26 revenue $3,178M (C) | $3,130M: 0.72; $3,240M: 0.42 |
| Joint bear-for-YES (GBV 11, u 20, migration 0) | 0.86 |
| Joint bull-for-NO (GBV 15.2, u 15, migration 2) | 0.07 |
| Mixture weights 0.45/0.30/0.25 | all Route A: 0.46; all Route B: 0.68; all Route C: 0.59 |

Pre-mortem ("it is 5 Nov and unearned fees printed −1% to +2%"): (1) the unpaid share stalled at ~15% because the July expansion was small and RNPL take-up outside the US plateaued — the main NO path (u 15 rows: 0.20–0.27); (2) GBV printed +15% or better, lifting the line 2 points (Route A at Street GBV: 0.30); (3) the seasonal reading is wrong the other way — at 30 Sep more of the backlog is near-dated Q4 stays whose RNPL payment dates have already passed, so u is *lower* at 30 Sep than at 30 Jun (not modelled; would move Route A to ~0.30); (4) the migration lift was larger (a +2 to +3 point effect at a 70% migrated share with full pass-through). "It printed −6% or worse": u ≥ 20% with team GBV (0.64–0.79). Asymmetry: this line is the pre-registered RNPL evidence item; a YES that resolves NO would be read as the deferral thesis failing, whereas the D1 row itself says the line "cannot separate" deferral from cancellation, so the log keeps 0.55 rather than the 0.6–0.7 the sequential route alone would give.

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-17 to 2026-10-02 | September Inside Airbnb dumps; 3Q26 nights/GBV band refreshed | Re-run Route A at the new GBV: each +1pt of GBV growth ≈ −0.08 on Route A, −0.04 on the final |
| 2026-10-02 | Prelim memo due | Quote 0.55 (0.40–0.70), median $1,755M; state the decomposition (deferral −17, migration +1, FX 0 on GBV +13) and that the −3% row is a payment-timing read |
| 2026-10-13 | EEA/CH single-fee deadline | Migration term to the top of its range if completion is confirmed (final −0.03) |
| 2026-10-15 to 2026-11-03 | Any management remark on RNPL share, eligibility or cash timing (conferences, previews) | A stated RNPL GBV share ≥ 25% → u 20 (final ~0.65); share flat at ~20% → u 15–16 (final ~0.35) |
| 2026-11-05 (after close) | 3Q26 letter (unearned-fees sentence, RNPL share) and 10-Q (balance sheet "Unearned fees"; six-/nine-month cash-flow line) | Resolve on the 10-Q; score the audit's corrected rule (UF y/y − GBV y/y: ≤ −18 drag on, −12 to −18 in line, > −8 weakened); re-solve u on the new print |
| 10-Q filing date if later than 5 Nov | 10-Q | Resolution moves with the filing |

RESUME: the next agent (audit response) should re-run `datasets/c12_model.py` (deterministic, ~30 s), check claim 1's series against the 10-Qs (the panel is XBRL-derived), and attack the three judgement inputs: u_3Q26 N(18, 3) (the 15 vs 20 rows span 0.20–0.79), the u_3Q25 base of 3.5% (from the 3Q25 gap of −4.1 points; 5% moves Route A to 0.32), and the migration sign and size (+1.0 ± 0.7, from the 10-K accounting and the fee-takerate migrated-share path). The reading of D038 as a flow statement (convention 4) should be tested against the 3Q26 letter's wording on 5 Nov.
