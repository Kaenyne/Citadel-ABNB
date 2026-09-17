# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable). Batch A15 (B04, B05, B06, B07). Reproduction: `datasets/ntto_overseas_monthly_2023_2026-07.csv`, `datasets/ntto_overseas_quarterly.csv` and `datasets/ntto_q4_persistence.csv` are produced from `data/processed/q3nowcast/G/raw/ntto_arrivals_monthly.csv` (region = OVERSEAS) by the pandas snippet described in query 3; the probabilities in section 5 are normal-CDF evaluations on the stated centre and sd.

## 0. Metadata
- question_name: bonus-us-inbound-falls
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § B07)
- type: binary
- run_mode: initial
- run_date: 2026-09-17
- open_date: 2026-09-17
- close_date: 2027-02-15
- resolution_date: 2027-02-15
- scoring: spot
- cp_visible: no
- cp_value: n/a
- revision: 1
- agent: fable
- batch: A15

## 0b. Question (verbatim)
### Title
Will NTTO's overseas (non-Canada/Mexico) visitor arrivals to the US for 4Q26 be ≤ −5% y/y?
### Resolution Criteria
**Type.** Binary. **Resolution.** Yes if the sum of Oct–Dec 2026 overseas arrivals (NTTO I-94 monthly) ÷ Oct–Dec 2025 − 1 ≤ −0.05. Resolution ~Feb 2027 when December data posts.
### Fine Print
None beyond the resolution sentence. Conventions adopted: (1) "overseas" is NTTO's published Overseas total in the I-94 Country-of-Residence monthly table (all regions except Canada and Mexico; the same series as `data/processed/q3nowcast/G/raw/ntto_arrivals_monthly.csv`, region OVERSEAS); (2) the numerator uses the December 2026 preliminary release if the final is not posted by resolution, and the denominator uses the Oct–Dec 2025 figures as they stand in that same release (NTTO revises prior months); (3) if a federal shutdown delays the December posting past mid-February, the same computation applies on the actual posting date.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | NTTO overseas arrivals, monthly y/y: Jan 2026 −4.2%, Feb +0.8, Mar +3.6, Apr −14.1, May −6.5, Jun −1.8, Jul −7.0 (preliminary); quarterly: 1Q26 −0.05%, 2Q26 −7.67%; Jan–Jul 2026 −4.74% (18.33m vs 19.24m) | datasets/ntto_overseas_monthly_2023_2026-07.csv; data/processed/q3nowcast/G/raw/ntto_arrivals_monthly.csv (NTTO COR monthly, pulled 2026-09-11) | 2026-08 | 2026-09-17 | yes |
| 2 | The 4Q25 base was itself weak but less weak than 3Q25: 3Q25 −4.40%, 4Q25 −2.55% (Oct −3.1, Nov −3.5, Dec −1.3); 4Q25 two-year stack +3.2% (4Q24 was +5.9%) | datasets/ntto_overseas_quarterly.csv | 2026-08 | 2026-09-17 | yes |
| 3 | Two-year stacks in 2026 (vs the same month of 2024): Jan +0.9%, Feb −1.7, Mar −8.5, Apr −7.2, May −9.1, Jun −5.2 (World Cup group stage), Jul −9.9; the war-era level is −7 to −10 ex-June | computed from claim 1 | 2026-09-17 | 2026-09-17 | yes |
| 4 | Regional composition of 4Q25 overseas: Western Europe 36.3% (Jul 2026 y/y −10.5%, 2Q26 −11.6%), Asia 23.9% (−7.8%, −7.4%), South America 17.2% (+2.3%, +1.9%), Central America 6.2% (−13.1%), Caribbean 5.5% (−7.5%), Oceania 3.2% (−7.7%), Eastern Europe 3.2% (+1.3%), Middle East 3.1% (+3.5%, after −33%/−31% in Mar/Apr), Africa 1.4% (−18.4%) | computed from claim 1 | 2026-09-17 | 2026-09-17 | yes |
| 5 | Persistence statistics (18 years, 2004-2019 and 2024-2025): Q4 y/y minus Q3 y/y mean −0.5pp, sd 4.0, MAD 2.4; Q4 minus July mean −1.0, sd 6.3, MAD 3.4; Q4 minus Q2 mean −2.3, sd 7.4, MAD 2.8 | datasets/ntto_q4_persistence.csv | 2026-09-17 | 2026-09-17 | yes |
| 6 | No August 2026 file exists yet on trade.gov (latest links: FINAL June, Preliminary July); the guessed August URL returned 404; NTTO's Sep prelim is expected mid-October and December's in February | sources/i94_arrivals_program_page_2026-09-17.html; sources/web_search_notes_2026-09-17.md | 2026-09-17 | 2026-09-17 | yes |
| 7 | Drivers still in force: Gulf-hub disruption (BA/KLM suspensions to 24-25 Oct, EASA warnings to 30 Sep, Middle Eastern carriers −14% demand), oil $108 and CPI airline fares +21% y/y in 3Q26 (from +24.6% in 2Q26), American 4Q26 transatlantic capacity +1.8% and Pacific −2.9%, IAG flat, Air France-KLM cut twice; TSA throughput −3.7% y/y (Aug) | docs/pitch-forecasts/questions/bonus-geopolitical-headwind-cited/sources/web_fetch_notes_2026-09-17.md; research/notes/overnight/05_macro-outlook-and-transmission.md §4.4 | 2026-09-16 | 2026-09-17 | yes |
| 8 | Policy drivers now lapping: the $250 visa integrity fee took effect 1 Oct 2025 and the ESTA fee rose 30 Sep 2025, so 4Q26 is the first quarter to lap them; Tourism Economics puts the fee's effect at about 1m visitors a year; the 50% tariff on Canadian imports (Sep 2026) is a Canada story and outside the overseas series | research/notes/overnight/05_macro-outlook-and-transmission.md §4.6; sources/web_search_notes_2026-09-17.md | 2026-09-05 | 2026-09-17 | yes |
| 9 | The World Cup was a June-July 2026 event (group-stage arrivals +0.2% y/y per NTTO via Forbes) and is not in 4Q26; the 2027 comparison problem is 2Q27/3Q27 | research/notes/overnight/05_macro-outlook-and-transmission.md §4.6 | 2026-09-05 | 2026-09-17 | no |
| 10 | External forecast (Tourism Economics/Brand USA, Sep 2026): 2026 international arrivals +2.4% (cut from +3.4%); overseas 42.6m in 2026 and 45.7m in 2027; "overseas arrivals came in below last year as of July 2026"; the definition differs from the I-94 COR overseas series (34.3m in 2025) and the 2026 growth view is inconsistent with −4.7% YTD, so it gets zero weight as a level anchor | sources/web_search_notes_2026-09-17.md | 2026-09 | 2026-09-17 | no |
| 11 | NTTO series in the team's nowcast: ntto_total_full and ntto_overseas_qtd1m are survivors with RMSE ratios 0.72-0.74x naive on 3Q26 nights (2023Q1-2026Q2, n 14); 3Q26 feature readings ntto_overseas_full −7.7%, ntto_overseas_qtd1m −14.1% (Apr) → −7.0% (Jul) | data/processed/q3nowcast/G/G_backtest_survivors.csv; G_feature_readings_3q26.csv | 2026-09-11 | 2026-09-17 | no |
| 12 | Inbound to the US is 2-3% of Airbnb's business (management, 1Q25 call); BEA inbound spending ran −4.8% to −8.6% for five quarters while NA nights accelerated; AirDNA: international demand for US STRs fell 13 consecutive months before the World Cup, −12% in the July 2026 midyear update | research/notes/overnight/05_macro-outlook-and-transmission.md §3 regional table and §4.6; data/processed/overnight/11_supply_economics.csv (airdna_us_2026_outlook_jul) | 2026-09-05 | 2026-09-17 | yes (impact) |
| 13 | No prediction market exists on NTTO arrivals (Polymarket/Kalshi scans in the A04/A09 logs and this batch found none) | docs/pitch-forecasts/questions/risk-q3-nights-meets-guide/research-log.md; sources/ | 2026-09-17 | 2026-09-17 | no |
| 14 | Final recency check (17 Sep): no new NTTO release; no new inbound policy change announced this week; Gulf disruptions unchanged | sources/web_search_notes_2026-09-17.md; B06 sources | 2026-09-17 | 2026-09-17 | no |

## 2. Query Log
1. [repo] data/processed/q3nowcast/G/raw/ntto_arrivals_monthly.csv (full read; regions, 2024-2026 matrix)
2. [repo] data/processed/q3nowcast/G/G_backtest_survivors.csv, G_feature_readings_3q26.csv, source_inventory.csv grep "ntto"
3. [computed] overseas monthly y/y, quarterly sums and y/y (complete quarters only), two-year stacks, regional shares and y/y, Q4-minus-Q3/Jul/Q2 persistence table (pandas), saved to datasets/
4. [repo] research/notes/overnight/05_macro-outlook-and-transmission.md §3, §4.4, §4.6
5. [repo] data/processed/overnight/11_supply_economics.csv (AirDNA inbound rows)
6. [curl] trade.gov/i-94-arrivals-program (200, saved); guessed 2026-09 August preliminary and July final URLs (404, deleted)
7. WebSearch: NTTO international arrivals August 2026 overseas visitors
8. WebSearch: US international visitor arrivals decline 2026 visa fee tariffs overseas travel forecast fourth quarter
9. WebFetch: congress.gov CRS IN12589 (403)
10. WebSearch: Tourism Economics forecast overseas arrivals United States 2026 2027 decline September 2026
11. WebFetch: travelweekly.com Brand USA forecast article (403; snippet only)
12. [shared with B06] WebSearch "Gulf Hormuz news today" (final 72-hour recency check on the decisive driver; nothing new)

## 3. Leading Hypothesis Entities
NTTO, I-94, overseas arrivals, Western Europe, Asia, Gulf hubs, airfares, visa integrity fee, Tourism Economics

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| War-era two-year stack (−7 to −10) persists through Q4 → 4Q26 y/y ≈ −5.6% (stack −8 on a −2.55% base) | base case (about 0.55 weight) | Gulf-route suspensions to late October, oil $108, fares +21%, Western Europe −10.5% in July (claims 3, 4, 7); nothing in the September data says the shock is fading yet |
| Partial normalisation (stack −6 → y/y −3.5%) as the Middle East region recovers, the visa/ESTA fees lap and the dollar is weaker y/y | kept (about 0.30) | Middle East arrivals back to +3.5% in July; BEA inbound improved from −4.8% to −0.4% in 2Q26 (claim 12); 4Q25 was itself weak |
| Further deterioration (stack −10 or worse → y/y ≤ −8%) from a new escalation, airline winter-schedule cuts, or a shutdown-related visa slowdown | kept (about 0.15) | Airlines cut long-haul 2027 plans; a new Gulf escalation would repeat March-April |
| External forecasts (Tourism Economics +2.4% 2026) imply a Q4 rebound | discarded | Definition differs; inconsistent with −4.7% YTD; "catching up with the actual data" (claim 10) |
| The World Cup distorts Q4 | discarded | June-July event (claim 9) |
| Data risk: a shutdown delays December data | kept as timing risk only | Convention 3 |

## 5. Independent Estimates
- base_rate_estimate: 0.65 — persistence: Q3 2026 estimate ≈ −6.5% (Jul −7.0 preliminary; August unknown; September faces a −7.7% comp) plus the historical Q4-minus-Q3 mean −0.5 → centre −7.0, sd 4.0 (claim 5) → P(≤ −5) = Φ((−5 + 7)/4) = Φ(0.50) = 0.69; using the robust MAD-based sd (3.6): 0.71; using Q4-minus-July on Jul −7.0 (centre −8.0, robust sd 5.0): 0.73; averaging with a 30% mean-reversion pull toward the pre-war level (0%): centre −5.0, sd 4 → 0.50. Blend 0.65
- decomposition_estimate: 0.57 — scenario mixture on the two-year stack (claim 3) converted through the −2.55% base (claim 2): persist −8 (weight 0.55, y/y −5.6, within-scenario sd 2.0), normalise −6 (0.30, −3.5, sd 2.0), deteriorate −10.5 (0.15, −8.2, sd 2.0); P(≤ −5) = 0.55 × Φ(0.3) + 0.30 × Φ(−0.75) + 0.15 × Φ(1.6) = 0.55 × 0.62 + 0.30 × 0.23 + 0.15 × 0.95 = 0.34 + 0.07 + 0.14 = 0.55; with the Western Europe weight (36%) at −10% and Asia at −8% held to Q4 the centre is −6.5 and the same mixture gives 0.60; report 0.57
- anchor_estimate: none — no market; the external forecast is stale and on a different definition (claim 10)
- anchor_value: n/a (NO_EXTERNAL_ANCHOR)
- final_estimate: 0.58 (credible interval 0.42–0.72)
- final_minus_anchor: n/a. The base rate (0.65) and decomposition (0.57) differ by 8 points because the persistence class ignores the easier-than-Q3 comparison (4Q25 −2.55 vs 3Q25 −4.40, a 1.9pp headwind to the Q4 y/y relative to Q3) and the lapping of the October 2025 fee changes; the final leans to the decomposition, which carries both

## 6. Final Numbers
P(Yes) = 0.58; credible interval 0.42–0.72.
Extreme-probability gate: not triggered.
Coherence: B07 and R11/B15 (US RevPAR) share the inbound channel only weakly (inbound is a small share of US hotel demand); B07 is independent of the 5 Nov print questions.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Two-year stack persists at −8 (weight 0.55) | August preliminary (mid-October) prints ≤ −8% y/y: weights 0.65/0.15/0.20 → 0.70; August ≥ −3%: weights 0.35/0.50/0.15 → 0.42 |
| Gulf-route suspensions end late October as scheduled | Extended into December: +0.06; a ceasefire and Hormuz reopening by mid-October: −0.10 (Asia and Middle East corridors) |
| Western Europe (36% of overseas) stays at −10% | If Western Europe improves to −5% in Q4 (intra-European substitution fades after summer): centre −4.6 → 0.45 |
| 4Q25 base −2.55% as currently published | NTTO revises 4Q25 up by 1pp in the December release: −0.05; down by 1pp: +0.05 |
| Within-scenario sd 2.0 | sd 3.0: 0.56; sd 1.5: 0.58 |
| Resolution uses preliminary December data | Preliminary counts have been revised by up to ±1pp at the monthly level; no directional bias assumed |

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| ~2026-10-10 | NTTO August 2026 preliminary (COR) | ≤ −8%: 0.70; −8 to −5: hold; ≥ −3%: 0.42 |
| 2026-10-13 | September CPI airline fares | Fares y/y falling below +10%: −0.03 |
| 2026-10-24/25 | KLM/BA Gulf resumptions | Resumed: −0.03; extended: +0.06 |
| ~2026-11-10 | NTTO September preliminary (completes Q3) | Recompute the Q3 y/y and re-centre the persistence class; each 1pp on Q3 moves P by about 0.08 |
| ~2026-12-10 | NTTO October preliminary (first Q4 month) | October ≤ −6%: 0.75; ≥ −3%: 0.35 |
| ~2027-01-10 | November preliminary | Two months in hand: snap toward 0.9/0.1 unless December's comp (−1.3%, the easiest of the quarter) can flip the sum |
| ~2027-02-10 | December preliminary | Resolve per conventions 1-3; if delayed by a shutdown, hold until posted |

## 9. Impact
If B07 resolves Yes, the informative content is that overseas arrivals ran about 3pp weaker than the memo's implicit path (about −2%, i.e. the 4Q25 rate). Deltas versus the memo's base case:

| Item | Delta if B07 happens | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | 0.0 | Q3 is printed before resolution; the July reading is already inside the nowcast stack (claim 11) |
| 4Q26 nights (pts) | **−0.08** (3pp × 2.5% inbound share of nights; claim 12) | management 1Q25; brief sensitivity |
| ADR (pts) | 0.0 (cross-border stays carry a higher ADR; a 0.08pt mix loss is below rounding) | |
| 4Q26 revenue ($M) | **−2** (0.08 × $30M) | brief sensitivity |
| FY27 revenue ($M) | **−10** (0.06pt × $158M) | brief sensitivity |
| FY26 adj. EBITDA margin (pp) | 0.0 | |
| FY27 adj. EBITDA margin (pp) | **−0.04** | brief sensitivity |
| FY27 EPS ($) | **−0.01** | brief sensitivity |
| Stock ($/share) | **−0.2** (0.06pt × $4.90, rounded; the "US inbound collapse" narrative is already in the stock via 2025) | brief sensitivity |
| **EV = P × impact** | **0.58 × −$0.2 = −$0.1/share** | |
| Materiality | **Immaterial.** Inbound is 2-3% of the business and the BEA/NTTO collapse of 2025 coincided with NA nights accelerating (claim 12). The memo should drop this as a number; it can keep one clause noting overseas arrivals are running −5 to −8% and that Airbnb's KPI has not responded to inbound before | |

## RESUME
The next agent (audit response) should re-run the persistence table (`datasets/ntto_q4_persistence.csv`) after the August preliminary lands (~10 Oct) and re-centre; check whether NTTO's I-94 "Overseas" total in the COR workbook matches the OVERSEAS region in the team cache (it should, to the unit); and attack the 0.55/0.30/0.15 scenario weights, which are judgement. The impact table needs no rework: the question is immaterial to the stock under any weighting.
