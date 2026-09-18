# RESEARCH LOG

Revision 2 (2026-09-17, audit response to A15, Fable). Revision 1 (2026-09-17, initial forecast, Fable). Batch A15 (B04, B05, B06, B07). Reproduction: `datasets/ntto_overseas_monthly_2023_2026-07.csv`, `datasets/ntto_overseas_quarterly.csv` and `datasets/ntto_q4_persistence.csv` are produced from `data/processed/q3nowcast/G/raw/ntto_arrivals_monthly.csv` (region = OVERSEAS) by the pandas snippet described in query 3 (the audit reproduced all 18 rows to 0.00); revision 2 adds `datasets/scenario_mixture_v2.csv` and `datasets/constant_july_stack_backtest_v2.csv`; the probabilities in section 5 are normal-CDF evaluations on the stated centre and sd; the audit's `docs/pitch-forecasts/audits/A15-reproduce.py` replays every figure in claims 1-5 and the centres in claim 15.

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
- revision: 2
- revised: 2026-09-17
- agent: fable
- batch: A15
- audit: `docs/pitch-forecasts/audits/A15-research-audit.md` (independent Opus auditor standing in for Codex); response `docs/pitch-forecasts/audits/A15-audit-response.md`

## 0b. Question (verbatim)
### Title
Will NTTO's overseas (non-Canada/Mexico) visitor arrivals to the US for 4Q26 be ≤ −5% y/y?
### Resolution Criteria
**Type.** Binary. **Resolution.** Yes if the sum of Oct–Dec 2026 overseas arrivals (NTTO I-94 monthly) ÷ Oct–Dec 2025 − 1 ≤ −0.05. Resolution ~Feb 2027 when December data posts.
### Fine Print
None beyond the resolution sentence. Conventions adopted: (1) "overseas" is NTTO's published Overseas total in the I-94 Country-of-Residence monthly table (all regions except Canada and Mexico; the same series as `data/processed/q3nowcast/G/raw/ntto_arrivals_monthly.csv`, region OVERSEAS — validated at revision 2, claim 16); (2) the numerator uses the December 2026 preliminary release if the final is not posted by resolution, and the denominator uses the Oct–Dec 2025 figures as they stand in that same release (NTTO revises prior months); (3) if a federal shutdown delays the December posting past mid-February, the same computation applies on the actual posting date.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | NTTO overseas arrivals, monthly y/y: Jan 2026 −4.21%, Feb +0.79, Mar +3.56, Apr −14.12, May −6.54, Jun −1.85, Jul −7.02 (preliminary); quarterly: 1Q26 −0.05%, 2Q26 −7.67%; Jan–Jul 2026 −4.74% (18.33m vs 19.24m) | datasets/ntto_overseas_monthly_2023_2026-07.csv; data/processed/q3nowcast/G/raw/ntto_arrivals_monthly.csv (NTTO COR monthly, pulled 2026-09-11) | 2026-08 | 2026-09-17 | yes |
| 2 | The 4Q25 base was itself weak but less weak than 3Q25: 3Q25 −4.40% (Jul −3.09, Aug −2.85, **Sep −7.69**), 4Q25 −2.55% (Oct −3.12, Nov −3.47, Dec −1.28); 4Q25 two-year stack +3.22% (4Q24 was +5.93%). **September 2025 is the weakest month of 3Q25 and therefore the easiest 3Q26 comparison; the 4Q25 base (−2.55) is a harder comparison than 3Q25 (−4.40): for a given two-year stack it costs the Q4 y/y about 1.85pp relative to Q3** | datasets/ntto_overseas_quarterly.csv | 2026-08 | 2026-09-17 | yes |
| 3 | Two-year stacks in 2026 (vs the same month of 2024): Jan +0.93%, Feb −1.68, Mar −8.49, Apr −7.24, May −9.11, Jun −5.18 (World Cup group stage), Jul −9.89; the war-era level is −7 to −10 ex-June; the Mar–Jul mean ex-June is **−8.68**, including June −7.98; July's −9.89 is the single worst reading and the first month after the World Cup final (19 Jul), so part of it may be displacement into June | computed from claim 1 | 2026-09-17 | 2026-09-17 | yes |
| 4 | Regional composition of 4Q25 overseas: Western Europe 36.3% (Jul 2026 y/y −10.5%, 2Q26 −11.6%), Asia 23.9% (−7.8%, −7.4%), South America 17.2% (+2.3%, +1.9%), Central America 6.2% (−13.1%), Caribbean 5.5% (−7.5%), Oceania 3.2% (−7.7%), Eastern Europe 3.2% (+1.3%), Middle East 3.1% (+3.5%, after −33%/−31% in Mar/Apr), Africa 1.4% (−18.4%) | computed from claim 1 | 2026-09-17 | 2026-09-17 | yes |
| 5 | Persistence statistics (18 years, 2004-2019 and 2024-2025): Q4 y/y minus Q3 y/y mean −0.49pp, sd 4.04, MAD 2.42; Q4 minus July mean −1.00, sd 6.34, MAD 3.38; Q4 minus Q2 mean −2.25, sd 7.43, MAD 2.76 | datasets/ntto_q4_persistence.csv | 2026-09-17 | 2026-09-17 | yes |
| 6 | No August 2026 file exists yet on trade.gov (latest links: FINAL June, Preliminary July); the guessed August URL returned 404; the saved program page (HTTP 200) shows the 8th/18th/28th Advance/Preliminary/Final cadence, so the Sep prelim is expected mid-October and December's in February | sources/i94_arrivals_program_page_2026-09-17.html; sources/web_search_notes_2026-09-17.md | 2026-09-17 | 2026-09-17 | yes |
| 7 | Drivers still in force: Gulf-hub disruption (BA/KLM suspensions to 24-25 Oct, EASA warnings to 30 Sep, Middle Eastern carriers −14% demand), oil $108 and CPI airline fares +21% y/y in 3Q26 (from +24.6% in 2Q26), American 4Q26 transatlantic capacity +1.8% and Pacific −2.9%, IAG flat, Air France-KLM cut twice; TSA throughput −3.7% y/y (Aug) | docs/pitch-forecasts/questions/bonus-geopolitical-headwind-cited/sources/web_fetch_notes_2026-09-17.md; research/notes/overnight/05_macro-outlook-and-transmission.md §4.4 | 2026-09-16 | 2026-09-17 | yes |
| 8 | Policy drivers now lapping: the $250 visa integrity fee took effect 1 Oct 2025 and the ESTA fee rose 30 Sep 2025, so 4Q26 is the first quarter to lap them; Tourism Economics puts the fee's effect at about 1m visitors a year; the 50% tariff on Canadian imports (Sep 2026) is a Canada story and outside the overseas series. **The two-year-stack framework already embeds the lapping** (the stack compares 4Q26 with the pre-fee 4Q24 and the y/y automatically laps 4Q25), so no separate mean-reversion credit is taken for it | research/notes/overnight/05_macro-outlook-and-transmission.md §4.6; sources/web_search_notes_2026-09-17.md | 2026-09-05 | 2026-09-17 | yes |
| 9 | The World Cup was a June-July 2026 event (group-stage arrivals +0.2% y/y per NTTO via Forbes) and is not in 4Q26; the 2027 comparison problem is 2Q27/3Q27 | research/notes/overnight/05_macro-outlook-and-transmission.md §4.6 | 2026-09-05 | 2026-09-17 | no |
| 10 | External forecast (Tourism Economics/Brand USA, Sep 2026): 2026 international arrivals +2.4% (cut from +3.4%); overseas 42.6m in 2026 and 45.7m in 2027; "overseas arrivals came in below last year as of July 2026"; the definition differs from the I-94 COR overseas series (34.3m in 2025) and the 2026 growth view is inconsistent with −4.7% YTD, so it gets zero weight as a level anchor | sources/web_search_notes_2026-09-17.md | 2026-09 | 2026-09-17 | no |
| 11 | NTTO series in the team's nowcast: ntto_total_full and ntto_overseas_qtd1m are survivors with RMSE ratios 0.72-0.74x naive on 3Q26 nights (2023Q1-2026Q2, n 14); 3Q26 feature readings ntto_overseas_full −7.7%, ntto_overseas_qtd1m −14.1% (Apr) → −7.0% (Jul) | data/processed/q3nowcast/G/G_backtest_survivors.csv; G_feature_readings_3q26.csv | 2026-09-11 | 2026-09-17 | no |
| 12 | Inbound to the US is 2-3% of Airbnb's business (management, 1Q25 call); BEA inbound spending ran −4.8% to −8.6% for five quarters while NA nights accelerated; AirDNA: international demand for US STRs fell 13 consecutive months before the World Cup, −12% in the July 2026 midyear update | research/notes/overnight/05_macro-outlook-and-transmission.md §3 regional table and §4.6; data/processed/overnight/11_supply_economics.csv (airdna_us_2026_outlook_jul) | 2026-09-05 | 2026-09-17 | yes (impact) |
| 13 | No prediction market exists on NTTO arrivals (Polymarket/Kalshi scans in the A04/A09 logs and this batch found none) | docs/pitch-forecasts/questions/risk-q3-nights-meets-guide/research-log.md; sources/ | 2026-09-17 | 2026-09-17 | no |
| 14 | Final recency check (17 Sep): no new NTTO release; no new inbound policy change announced this week; Gulf disruptions unchanged **in the searches recorded** | sources/web_search_notes_2026-09-17.md; B06 sources | 2026-09-17 | 2026-09-17 | no |
| 15 | Centres for 4Q26 y/y recomputed from the cache: (a) Q3 persistence: 3Q26 at July's stack held through Aug-Sep = **−5.75%** (at the war-era ex-June mean stack −8.68: −4.91%), plus the historical Q4−Q3 mean −0.49 → **−6.24**; (b) aggregate constant-July-stack **−7.53**; (c) regional constant-July-stack on nine regions at 4Q25 weights **−7.08**; (d) 4Q25-share-weighted July y/y **−6.83**. Stack-to-y/y conversion through the −2.55% base: −6.5 → −4.05, −8.0 → −5.59, −8.68 → −6.29, −9.89 → −7.53, −11.0 → −8.67. **Estimator quality:** a naive constant-July-stack forecast of the Q4 y/y has error mean −1.16, **sd 7.39** over 16 years (`constant_july_stack_backtest_v2.csv`; the Q4 stack minus the July stack has sd 7.83), against sd 4.04 for the Q4−Q3 persistence class, so routes (b)-(d), which hold a single month's stack, are the noisier family | datasets/constant_july_stack_backtest_v2.csv; A15-reproduce.py | 2026-09-17 | 2026-09-17 | yes |
| 16 | The team cache is NTTO's published Overseas series: the saved search notes carry four published figures the cache reproduces — Jan 2026 overseas −4.2% (cache −4.21), Jan–May 2026 −4.8% (−4.78), 2025 overseas level 34.3m (34.29m), 2025 total international −5.5% (−5.55) | sources/web_search_notes_2026-09-17.md; A15-reproduce.py | 2026-09 | 2026-09-17 | yes |

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
13. [rev 2, computed] 2025 monthly y/y (Jul-Dec), 3Q26 at held stacks, four 4Q26 centres, constant-July-stack backtest 2005-2019 and 2025 (`constant_july_stack_backtest_v2.csv`), scenario table (`scenario_mixture_v2.csv`)
14. [rev 2, repo] docs/pitch-forecasts/audits/A15-reproduce.py run from the repo root (`py -3.13 -B`), output in `A15-reproduce.stdout.txt` (external validation of the cache, claim 16)

## 3. Leading Hypothesis Entities
NTTO, I-94, overseas arrivals, Western Europe, Asia, Gulf hubs, airfares, visa integrity fee, Tourism Economics

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| War-era two-year stack persists at its Mar–Jul ex-June mean (−8.7) through Q4 → 4Q26 y/y ≈ −6.3% | base case (weight 0.45) | Gulf-route suspensions to late October, oil $108, fares +21%, Western Europe −10.5% in July (claims 3, 4, 7); nothing in the September data says the shock is fading; July alone (−9.9) is the post-World-Cup month and is not taken as the trend |
| Partial normalisation (stack −6.5 → y/y −4.1%) as the Middle East region recovers, Gulf routes resume in late October and the dollar is weaker y/y | kept (0.30) | Middle East arrivals back to +3.5% in July; BEA inbound improved from −4.8% to −0.4% in 2Q26 (claim 12); Booking "starting to normalize" |
| Further deterioration (stack −11 → y/y ≤ −8.7%): July's −9.9 is the true trend plus airline winter-schedule cuts, a new escalation, or a shutdown-related visa slowdown | kept (0.25) | July is the latest reading; airlines cut long-haul 2027 plans; a new Gulf escalation would repeat March-April |
| External forecasts (Tourism Economics +2.4% 2026) imply a Q4 rebound | discarded | Definition differs; inconsistent with −4.7% YTD; "catching up with the actual data" (claim 10) |
| The World Cup distorts Q4 | discarded | June-July event (claim 9) |
| A separate mean-reversion pull toward the pre-war level for the lapping of the Oct 2025 fees | discarded at revision 2 | Already inside the two-year-stack framework (claim 8); revision 1 counted it twice |
| Data risk: a shutdown delays December data | kept as timing risk only | Convention 3 |

## 5. Independent Estimates
- base_rate_estimate: 0.63 — persistence class: Q3 2026 estimate **−5.75%** (July −7.02 preliminary; August and September unknown and held at July's two-year stack; September faces the easiest comp of the quarter, −7.69%) plus the historical Q4-minus-Q3 mean −0.49 → centre −6.24, sd 4.04 (claim 5) → P(≤ −5) = Φ(1.24/4.04) = **0.62**; robust MAD-based sd 3.6: 0.635; Q4-minus-July on Jul −7.0 (centre −8.0, sd 6.34): 0.68. The revision-1 mean-reversion branch (0.50) is dropped (claim 8). Blend **0.63**
- decomposition_estimate: 0.64 — scenario mixture on the two-year stack (claim 3) converted through the −2.55% base (claim 2; `scenario_mixture_v2.csv`): persist at the war-era ex-June mean −8.7 (weight 0.45, y/y −6.3), normalise −6.5 (0.30, −4.05), deteriorate −11.0 (0.25, −8.7); within-scenario sd 3.0 (the empirical Q4−Q3 sd 4.04 less the between-scenario spread); P(≤ −5) = 0.45 × Φ(0.43) + 0.30 × Φ(−0.32) + 0.25 × Φ(1.22) = 0.45 × 0.666 + 0.30 × 0.376 + 0.25 × 0.889 = 0.300 + 0.113 + 0.222 = **0.635**, mixture centre −6.2. Holding July's stack instead (persist −9.9 / normalise −7.0 / deteriorate −11.5 at 0.45/0.35/0.20) gives centre −6.8 and 0.68–0.70, the audit's construction; a single normal on the mean of the four centres in claim 15 (−6.9, sd 4.2) gives 0.67. Report **0.64**
- anchor_estimate: none — no market; the external forecast is stale and on a different definition (claim 10)
- anchor_value: n/a (NO_EXTERNAL_ANCHOR)
- final_estimate: 0.63 (credible interval 0.47–0.77)
- final_minus_anchor: n/a. The base rate (0.63) and decomposition (0.64) now agree. Revision 1's 8-point gap (0.65 vs 0.57) was two errors of opposite sign: the base-rate route used a 3Q26 input of −6.5% that required the stack to worsen to −11.0, and the decomposition's "persist" scenario sat 1.9pp *better* than the latest stack while §5 called the harder Q4 comp "easier". Audit A15's independent 0.63 uses the held-July centre (−6.8) with the persistence dispersion (4.2); this log centres 0.6pp higher because the July reading is a single post-World-Cup month and the constant-July-stack estimator has sd 7.4 (claim 15); the two constructions land on the same number

## 6. Final Numbers
P(Yes) = 0.63; credible interval 0.47–0.77.
Extreme-probability gate: not triggered.
Coherence: B07 and R11/B15 (US RevPAR) share the inbound channel only weakly (inbound is a small share of US hotel demand); B07 is independent of the 5 Nov print questions.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Persist scenario at the war-era mean stack −8.7 (weight 0.45) | If July's −9.9 is taken as the persistence level (audit construction): 0.68; if August's preliminary (mid-October) prints ≤ −8% y/y: weights 0.40/0.15/0.45 → 0.72; August ≥ −3%: weights 0.35/0.50/0.15 → 0.48 |
| Gulf-route suspensions end late October as scheduled | Extended into December: +0.05; a ceasefire and Hormuz reopening by mid-October: −0.10 (Asia and Middle East corridors) |
| Western Europe (36% of overseas) stays at −10% | If Western Europe improves to −5% in Q4 (intra-European substitution fades after summer): centre −4.8 → 0.50 |
| 4Q25 base −2.55% as currently published | NTTO revises 4Q25 up by 1pp in the December release: −0.06; down by 1pp: +0.06 |
| Within-scenario sd 3.0 | sd 2.0: 0.67; sd 4.0: 0.61 |
| Q3 2026 input −5.75 (July stack held) | At the war-era mean stack (−4.91): persistence centre −5.4 → 0.54; at −6.5 (revision 1): 0.69 |
| Resolution uses preliminary December data | Preliminary counts have been revised by up to ±1pp at the monthly level; no directional bias assumed |

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| ~2026-10-10 | NTTO August 2026 preliminary (COR) | ≤ −8%: 0.72; −8 to −5: hold; ≥ −3%: 0.48 |
| 2026-10-13 | September CPI airline fares | Fares y/y falling below +10%: −0.03 |
| 2026-10-24/25 | KLM/BA Gulf resumptions | Resumed: −0.03; extended: +0.05 |
| ~2026-11-10 | NTTO September preliminary (completes Q3; the −7.69% comp is the easiest of the quarter, so a September print near −4% is on trend) | Recompute the Q3 y/y and re-centre the persistence class; each 1pp on Q3 moves P by about 0.08 |
| ~2026-12-10 | NTTO October preliminary (first Q4 month) | October ≤ −6%: 0.78; ≥ −3%: 0.38 |
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
| Stock ($/share) | **−0.3** (0.06pt × $4.90 = $0.29; the "US inbound collapse" narrative is already in the stock via 2025) | brief sensitivity |
| **EV = P × impact** | **0.63 × −$0.3 = −$0.19/share** | |
| Materiality | **Immaterial.** Inbound is 2-3% of the business and the BEA/NTTO collapse of 2025 coincided with NA nights accelerating (claim 12). The memo should drop this as a number; it can keep one clause noting overseas arrivals are running −5 to −8% and that Airbnb's KPI has not responded to inbound before | |

## 10. Revision notes
| Change | Finding |
|---|---|
| Metadata: revision 2, revised 2026-09-17; audit and response paths added | — |
| Claim 2 and §5: the 3Q26 input −6.5 (which needed a −11.0 stack) replaced by −5.75 (July's stack held); September 2025 (−7.69) named as the easiest comp of 3Q26; persistence centre −7.0 → −6.24 → 0.62 | A15-02 |
| §5 and §4: the "persist −8" scenario, which sat 1.9pp better than July, replaced by persist at the war-era ex-June mean −8.7 (y/y −6.3), normalise −6.5 (−4.05), deteriorate −11.0 (−8.7) at 0.45/0.30/0.25 with within-scenario sd 3.0 (`scenario_mixture_v2.csv`); centre −5.4 → −6.2; the sentence calling the 4Q25 base "easier than Q3" corrected to "harder" (a 1.85pp headwind for a given stack — an argument for a higher number); the held-July construction (centre −6.8, 0.68-0.70) reported as the sensitivity, with the reason for not adopting it (post-World-Cup single month; constant-July-stack estimator sd 7.39, `constant_july_stack_backtest_v2.csv`) | A15-03 |
| Claim 8 and §5: the revision-1 mean-reversion branch (0.50 at 30% weight) dropped — the two-year stack already laps the Oct 2025 fees | A15-03 (audit's closing note) |
| Claim 16 added: the cache validated against four published NTTO figures (Jan −4.2, Jan–May −4.8, 2025 level 34.3m, 2025 total −5.5); the RESUME's open question closed | audit §B07 "what the log does well" |
| §9: stock −0.2 → −0.3 (0.06 × $4.90 = $0.29); EV −$0.12 → −$0.19 | A15-24 |
| Claim 14: "in the searches recorded" | A15-25 |
| §7 and §8 thresholds recomputed on the revision-2 centre (August ≤ −8%: 0.72; ≥ −3%: 0.48; October ≤ −6%: 0.78; ≥ −3%: 0.38); Q3-input and July-persistence sensitivity rows added | A15-02, A15-03 |
| Final 0.58 (0.42–0.72) → **0.63 (0.47–0.77)**; audit's independent 0.63 matched | A15-02, A15-03 |

## RESUME
The next agent should re-run the persistence table and the scenario mixture after the August preliminary lands (~10 Oct) and apply the §8 thresholds; the September preliminary (~10 Nov) closes Q3 and re-centres the persistence class (each 1pp on Q3 ≈ 0.08 on P). The only judgement left in the number is the persist/normalise/deteriorate weighting and whether July's −9.9 stack or the Mar–Jul mean −8.7 is the trend — August's print settles that directly. The impact table needs no rework: the question is immaterial to the stock under any weighting. The audit's 0.63 and this log's 0.63 agree.
