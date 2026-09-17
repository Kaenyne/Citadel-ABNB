# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable 5.1, batch A12 with R10, R15, R16). Reproduction: [datasets/r11_model.py](datasets/r11_model.py) (`py -3.13`, numpy/scipy, deterministic, <1 s; writes `r11_path.csv`, `r11_views.csv`, `r11_sensitivity.csv`). Weekly STR series copied from the repo: [datasets/str_weekly_us_3q26_repo_copy.csv](datasets/str_weekly_us_3q26_repo_copy.csv).

## 0. Metadata
- question_name: risk-q4-us-revpar-strong
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § R11)
- type: binary
- run_mode: initial
- run_date: 2026-09-17
- open_date: 2026-09-16
- close_date: 2027-01-25
- resolution_date: 2027-01-25
- scoring: spot
- cp_visible: no
- cp_value: n/a
- revision: 1
- agent: fable

## 0b. Question (verbatim)
### Title
Will STR's US hotel RevPAR growth for 4Q26 (Oct–Dec, as reported by STR/CoStar in Jan 2027) be ≥ +4% y/y?
### Resolution Criteria
**Type.** Binary. **Resolution.** Yes if the quarterly (or the average of the three monthly) US RevPAR y/y ≥ 4.0%. Resolution ~25 Jan 2027.
### Fine Print
(none in the registry.) Conventions adopted: (1) the resolving series is CoStar/STR's US monthly "hotel performance" release (occupancy × ADR = RevPAR, all-US, y/y on the same-month basis STR reports); the October release lands ~20 Nov, November ~20 Dec, December ~22 Jan 2027, so the average of the three monthly y/y figures is the practical resolver (a simple mean; STR's own Q4 figure, if it publishes one in the full-year release, governs where both exist); (2) trade-press reprints (Lodging, Hotel Dive, Hospitality Net) of the STR release count as the source when costar.com is unreachable; (3) if STR revises a month, the values as published at the January read govern; (4) 4.0% exactly resolves Yes.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | CoStar/STR US weekly 3Q26: July month occ 69.7% (+2.3%), ADR $171.74 (+5.7%), RevPAR $119.77 (+8.2%; NYC ADR +24% on the World Cup final); weeks ending 1 Aug RevPAR +7.3%, 8 Aug +7.2% (18th straight weekly gain; 79 days of summer +7.4%, strongest since 2022), 15 Aug +6.2% (ADR +3.5%), 22 Aug +4.4% (ADR +2.3%), 29 Aug +1.7% (ADR +0.6%; slowest since April; Labor Day one week later), 5 Sep +16.1% (calendar mirror image, not a demand signal) | `data/processed/q3nowcast/G/str_weekly_us_3q26.csv` (Lodging Magazine / CoStar reprints, URLs inside); `research/notes/q3nowcast/G_external-sources-q3-read.md` §1 item 1 | 2026-08-06 to 2026-09-11 | 2026-09-17 | yes |
| 2 | CoStar/Tourism Economics forecast, 7–10 Aug 2026: FY2026 RevPAR +4.4% (raised from +2.8% on 2 Jun), demand +1.7%, ADR +3.1%, occupancy 63.1%; H1 2026 sold 11.4m incremental room-nights "fueled in part by the World Cup and America 250"; FY2027 RevPAR +2.1%, ADR +1.6%, demand +1.1%; supply +0.4% (2026) / +0.6% (2027); June 2027 RevPAR −0.8% on the World Cup comparison; June and July 2027 event offsets; luxury double-digit RevPAR in Q2 and Q3 2026; no quarterly or H2 path published | https://www.hotelnewsresource.com/article142436.html (CoStar forecast assumptions, 10 Aug 2026); `research/notes/overnight/05_macro-outlook-and-transmission.md` §4.5 | 2026-08-10 / 2026-09-06 | 2026-09-17 | yes |
| 3 | CoStar/TE June forecast (2 Jun 2026): FY26 RevPAR +2.8%, ADR +2.0%, occupancy 62.8%; "January–April RevPAR +4% year over year"; Q1 2026 RevPAR the highest on record; World Cup bookings "tracked below expectations"; TE's World Cup lift +1.7% RevPAR in June–July, +0.4% full-year | https://www.hoteldive.com/news/costar-tourism-economics-hotel-revpar-forecast-2026/821683/ ; https://www.hoteldive.com/news/fifa-world-cup-modest-revpar-growth-us-report/812826/ (search snippet) | 2026-06-02 | 2026-09-17 | yes |
| 4 | 4Q25 base: October 2025 RevPAR $110.35, −0.9% y/y (occupancy 65.8%, −2.4%; ADR +1.5%); week of 2–8 Nov 2025 +6.2% "came from a straightforward comparison" with the 2024 election week (STR's Collazo), the 39-day shutdown cost ~1.5m room-nights (similar to the prior 39 days, "minimal disruption"); two weeks to 29 Nov −0.3%; "US hotel performance declines continue throughout December" (CoStar headline); FY2025 occupancy 62.3% (−1.2%), ADR $160.54 (+0.9%), RevPAR $100.02 (−0.3%), first annual RevPAR decline since 2020 | https://str.com/press-release/us-hotel-performance-october-2025 (snippet); https://hoteldata.com/blogs/str-november-2025-hotel-performance/ ; https://www.hoteldive.com/news/hotel-occupancy-revpar-decline-2025/810212/ ; `research/notes/overnight/06_consumer-choice-and-willingness-to-pay.md` §1.2 | 2025-11 to 2026-01-22 | 2026-09-17 | yes |
| 5 | 2026 monthly hotel pricing: STR ADR Mar +3.8% (RevPAR +5.9%), Jul +5.7% (+8.2%); CPI lodging away from home Jan −1.9, Feb −1.1, Mar +2.5, Apr +4.4, May +5.0, Jun +4.7, Jul +2.8; July 2026 luxury RevPAR +17.7% vs economy +3.6% (barbelled) | `research/notes/overnight/06_consumer-choice-and-willingness-to-pay.md` §1.2 | 2026-09-06 | 2026-09-17 | yes |
| 6 | Operators at Q2: Marriott FY26 RevPAR raised to 3.0–3.5% (US & Canada +5.0% in Q2; World Cup ~45bp of FY global RevPAR; July +7% global, +8% US & Canada, +5% ex-World Cup, group "turned upwards"); Hilton raised to 3.0–3.5%; Hyatt 3.5–4.5% maintained, Q3 system-wide ~+3%; Wyndham 0–1%, Choice US 0–1.25%. An H1 near +4% inside a 3.0–3.5% FY implies operator H2 near +2.5% | `research/notes/overnight/05_macro-outlook-and-transmission.md` §4.5, §4.8; `data/processed/q3nowcast/G/intra_quarter_commentary.csv` rows 55, 58, 63 | 2026-07-28 to 2026-09-09 | 2026-09-17 | yes |
| 7 | Macro backdrop: unemployment 4.1%, payrolls +162k (Aug), claims −10% y/y, sentiment recession-adjacent (Michigan 55.2), Fed hiked 16 Sep to 3.75–4.00% with three more priced; TSA throughput −3.7% y/y (Aug) as fares ration air travel; CR expires 11 Dec 2026; midterms 3 Nov 2026 | `05_macro-outlook-and-transmission.md` §4.1, §4.4, §4.9; R10 log claim 10 | 2026-09-06 / 2026-09-16 | 2026-09-17 | yes |
| 8 | Hotel-RevPAR readthrough to ABNB: MAR/HLT RevPAR y/y vs nights y/y r 0.88 (post-2022 n 14), walk-forward RMSE ratio 0.665–0.70 vs naive (the strongest external family), but "since 2024 Airbnb's own recent growth beats every peer model"; BKNG guided Q3 room nights +3–5% vs Airbnb "low double digits"; US hotel prices ran negative for seven quarters while Airbnb's pricing residual rose — hotel ADR does not track the ADR residual | `research/notes/2026-09-06_predictive-study.md` §4; `data/processed/q3nowcast/G/G_backtest_scoreboard.csv`; `research/notes/adrq3/J_adr-pricing-residual-and-card-v2.md` §2; `05_macro` §4.8 | 2026-09-06 to 2026-09-11 | 2026-09-17 | yes |
| 9 | Model (this log): FY26 +4.4% with Q1 +3.8, Q2 4.5–6.0, Q3 4.5–6.0 implies 4Q26 +3.1% (range −0.2 to +6.4 across the grid); AR(1) from a +5.5 Q3 toward a +2 long run (φ 0.6) gives +4.0; calendar/base adjustments +0.8 (soft 4Q25 comp) −0.7 (midterm week vs the 2025 election comp) −0.2 (CR/shutdown risk) = −0.1; blended centre +3.5, sd 1.7 → P(≥4.0) 0.39; E[RevPAR | ≥4] = 5.2 | `datasets/r11_views.csv`, `r11_path.csv` | 2026-09-17 | 2026-09-17 | yes |
| 10 | Base rate: US quarterly RevPAR y/y ≥ +4% in 1 of 13 post-recovery quarters 2023Q2–2026Q2 (2026Q2 only; 2025 ran −1 to +1; 2024 +1 to +3), from the annual and monthly STR figures in claims 3–5 (quarterly values are approximations from monthly releases, not an STR quarterly table) | claims 3–5; `datasets/r11_model.py` | 2026-09-17 | 2026-09-17 | yes |
| 11 | No prediction market on US RevPAR exists (Polymarket/Kalshi searched in the batch's R10/R16 pulls); the domain anchor is the CoStar/TE forecast (claim 2) | R10 log claim 14 | 2026-09-17 | 2026-09-17 | no |
| 12 | Brief sensitivities: 1pt of 4Q26 nights ≈ $30M; 1pt of ADR ≈ $46M of quarterly revenue (3Q26 basis, ~$30M in Q4); FY27 revenue $158M/pt; FY27 EPS $0.0014 per $M EBITDA; $1.50/share per pt of FY27 nights (fixed multiple) | `docs/pitch-forecasts/00_BRIEF.md` | 2026-09-16 | 2026-09-17 | yes |
| 13 | Web recency: CoStar has not yet published the August 2026 monthly (the July monthly came 26 Aug; August expected ~25 Sep); the latest weekly reprint is the week ending 5 Sep (Lodging, 11 Sep); costar.com and str.com return 403 to fetchers | https://lodgingmagazine.com/?s=costar (list fetched 2026-09-17); WebSearch results | 2026-09-11 | 2026-09-17 | no |

Newest load-bearing source: the week-ending-5-Sep STR reprint (11 Sep, 6 days old) and the 10 Aug forecast (38 days old against a 130-day window; the next forecast revision is due in November — monitoring row 3).

## 2. Query Log
1. [repo] `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md`; skill files; example log; finished logs F01, R01, C08, C05, R08
2. [repo] `research/notes/overnight/05_macro-outlook-and-transmission.md` §4.1–4.9; `06_consumer-choice-and-willingness-to-pay.md` §1.2, data-status table; `research/notes/q3nowcast/G_external-sources-q3-read.md`; `data/processed/q3nowcast/G/str_weekly_us_3q26.csv`, `G_quarterly_panel.csv`, `G_backtest_scoreboard.csv`, `G_feature_readings_3q26.csv`, `intra_quarter_commentary.csv`, `source_inventory.csv`; `data/processed/forecast_methods/macro_pulls/review_capture/costar_us_weekly.csv`
3. [repo] `research/notes/2026-09-06_predictive-study.md`; `research/notes/predictive/02_peer-readthrough.md`; `research/notes/adrq3/J_adr-pricing-residual-and-card-v2.md`; `data/processed/adr/06_price_benchmarks.csv`; `data/processed/hotel_13_market_panel/`, `hotel_expanded_research/` (listing only: no US RevPAR history there)
4. WebSearch: CoStar U.S. hotel industry August 2026 RevPAR year over year monthly results
5. WebSearch: STR U.S. hotel RevPAR October 2025 November 2025 December 2025 year over year monthly
6. WebSearch: CoStar Tourism Economics U.S. hotel forecast fourth quarter 2026 RevPAR World Cup comparison 2027
7. WebFetch: str.com November/December 2025 releases, costar.com August 2026 monthly and forecast-assumptions pages (all 403)
8. WebSearch: U.S. hotel performance December 2025 RevPAR occupancy ADR full year 2025 STR CoStar
9. WebSearch: CoStar August 2026 U.S. hotel occupancy ADR RevPAR month lodgingmagazine OR hotelnewsresource OR hospitalitynet (final recency check for this question: nothing newer than the 11 Sep weekly)
10. WebFetch: hotelnewsresource.com article142436 (forecast assumptions, 10 Aug); hoteldive.com 821683 (June forecast); hoteldive.com 810212 (FY25); hotelmanagement.net FY25 (403); hoteldata.com Nov-2025 blog; dshhoteladvisors.com week ending 22 Aug; lodgingmagazine.com/?s=costar
11. [computed] `datasets/r11_model.py`

WebSearch calls charged to R11: 5 of 5.

## 3. Leading Hypothesis Entities
CoStar, STR, Tourism Economics, US hotel RevPAR, Marriott, Hilton, Labor Day, midterm elections, continuing resolution

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Summer strength (+5–8%) persists into Q4 on the soft 4Q25 base (Oct −0.9%, FY25 −0.3%) | kept, the Yes path (≈0.39) | the mid-August slope (+7 → +4, ADR +5.7 → +0.6) says the World Cup/summer premium is fading; the comp helps by ~+0.8pp |
| The CoStar/TE FY26 +4.4% arithmetically implies a Q4 near +3% | kept as the anchor (0.31) | H1 ≈ +4–5 and Q3 ≈ +5.5 leave Q4 at +3.1 on average; but the FY number is a stale point forecast that has been revised +1.6pp in two months (2.8 → 4.4) |
| Operator H2 guides (~+2.5%) are the better read | folded into the AR(1) long-run (+2) | system-wide global figures; US & Canada ran +5 in Q2/+8 in July for Marriott |
| Midterm election week and a December shutdown repeat 2024/2025 patterns | kept as adjustments (−0.7, −0.2) | Nov 2025 got +6.2% early-month "from a straightforward comparison" with election week 2024; Nov 2026 gives that back; CR to 11 Dec |
| Luxury-led barbell means aggregate RevPAR ≥4 while economy is flat | inside the centre | July luxury +17.7 vs economy +3.6; the aggregate is what resolves |
| US RevPAR is a good forecaster of ABNB Q4 nights | kept for the impact table only at a low slope | r 0.88 level but decoupled since 2024 (claim 8) |

## 5. Independent Estimates
- base_rate_estimate: 0.20 — unconditional post-recovery rate 1 of 13 quarters ≥ +4% (0.08, claim 10), regime-conditioned by the AR(1) two-step from the current +5.5 run rate toward the +2 long run (0.50 at φ 0.6); the two poles averaged, weight toward the regime because 2023–25 was a no-growth regime that the 2026 data have left
- decomposition_estimate: 0.39 — FY26-implied Q4 (+3.1) and AR(1) path (+4.0) averaged, plus the comp/election/CR adjustments (−0.1), sd 1.7pp (the scale of STR's own two-month forecast revision): centre +3.5 (claim 9)
- anchor_estimate: 0.31 — the CoStar/TE forecast's implied Q4 (+3.1, sd 1.7) with no calendar adjustment (claim 2); no tradable market (claim 11)
- anchor_value: 0.31 (CoStar/TE FY26 +4.4% of 10 Aug 2026 minus the H1/Q3 run rate; NO tradable market)
- final_estimate: 0.38 (credible interval 0.25–0.52)
- final_minus_anchor: +7 points. NOT_INDEPENDENTLY_DERIVED flag noted: the decomposition shares the FY26 forecast with the anchor; what moves the final above it is the AR(1) persistence of a +5–8% summer and the soft 4Q25 base (Oct −0.9%), which the stale FY point does not carry; what holds it below 0.5 is the mid-August deceleration to +4.4/+1.7 with ADR at +0.6% and the operators' H2 arithmetic (~+2.5%)

## 6. Final Numbers
**Binary.** P(STR US RevPAR 4Q26 y/y ≥ +4.0%) = **0.38**, credible interval **0.25–0.52**.
Implied distribution: centre +3.5%, sd 1.7; E[RevPAR | ≥4] = +5.2%; P(≤ +1.0%) = 0.07 (the mirror question B15); P(≤ 0) = 0.02.
Extreme-probability gate: not triggered.

## 7. Sensitivity
Rows from `datasets/r11_sensitivity.csv`.
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Q3 runs +5.5 (Jul 8.2, Aug ~5.5, Sep ~3) | Sep holds +6 (Q3 +6.5): FY-implied Q4 falls but the AR path rises: 0.30 on the model's arithmetic, ~0.45 if the FY forecast is also raised (the honest read: a stronger September raises P; the FY constraint is stale) |
| FY26 forecast +4.4 held through November | cut to +4.0: 0.19; raised to +4.8: 0.55 |
| Election-week and CR drags (−0.9 net) | none: 0.60; a December shutdown (−1.5): 0.11 |
| AR(1) persistence φ 0.6 | 0.8: 0.47; 0.4: 0.31 |
| sd 1.7 | 1.2: 0.34; 2.2: 0.41 |
| Joint bull (Q3 6.5, FY 4.8, no drag, φ 0.8) | 0.78 |
| Joint bear (Q3 4.5, FY 4.0, December shutdown) | 0.06 |

Pre-mortem ("it is 25 Jan 2027 and Q4 RevPAR printed ≥ +4%"): (1) the soft 4Q25 comp did more than +0.8pp (October 2025 was −0.9% with a shutdown and hurricane-market comps; a flat December 2026 against a −1% December 2025 is +1) — the comp adjustment is the least-measured input; (2) group and luxury carried the aggregate (Marriott: group "turned upwards", luxury +17.7% in July) while economy stayed flat; (3) rate held: ADR +3% rather than the +0.6% of late August. ("It printed ≤ +2%"): airfares rationing air travel (TSA −3.7%), the election week, a CR shutdown, and the World Cup/summer premium fully unwound. Asymmetry: the memo cites decelerating hotels as corroboration of an Airbnb deceleration; a strong Q4 RevPAR print would remove that line but does little to ABNB's own KPI (claim 8).

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| weekly (Thu) | CoStar weekly US results (Lodging reprint) | September weeks ≥ +5%: +0.03 each two weeks of confirmation; ≤ +2%: −0.03 |
| ~2026-09-25 | CoStar August 2026 monthly | August ≥ +6%: +0.03; ≤ +4%: −0.03 |
| 2026-10-02 | Prelim memo freeze | Quote 0.38 (0.25–0.52) with B15's mirror 0.07 |
| 2026-10-21 to 2026-11-03 | Hilton, Hyatt, Marriott Q3 prints; FY26 RevPAR guides | A second raise (to ≥ +3.5–4.0%): +0.05; a cut: −0.05 |
| ~2026-11-10 | CoStar/TE November forecast revision | Re-anchor on the new FY26 figure: each +0.4pp on FY26 ≈ +0.08 |
| 2026-11-03 | Midterms | No action; the −0.7 is priced |
| ~2026-11-20 | CoStar October monthly | October ≥ +4%: → ~0.55; ≤ +2%: → ~0.20 |
| 2026-12-11 | CR expiry | A shutdown: −0.15 |
| ~2026-12-20 | CoStar November monthly | Update the three-month mean arithmetic |
| ~2027-01-22 | CoStar December monthly / FY2026 release | Resolve on the mean of the three months (convention 1) |

## 9. Impact
If Yes (E[4Q26 RevPAR | ≥4] = +5.2% vs the base-case +3.5%, +1.7pp of US hotel RevPAR; a stay-date, US-only series):

| Item | Delta if R11 happens | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | 0 | Q4 series; Q3 resolves first |
| 4Q26 nights (pts) | **+0.4** (RevPAR→nights slope ~0.4 on the 2023–26 co-movement × 1.7pp, halved for the stay-date/bookings mismatch and NA's ~30% share of nights) | claim 8; judgement |
| ADR (pts) | **+0.3** (NA ADR co-moves with hotel ADR direction; the residual does not) | claim 8 |
| 4Q26 revenue ($M) | **+20** (0.4 × $30M + 0.3 × ~$30M) | claim 12 |
| FY27 revenue ($M) | **+30** (a stronger Q4 lifts 1Q27 recognised revenue via the kernel; STR's 2027 +2.1% is unchanged) | kernel carry |
| FY26 adj. EBITDA margin (pp) | +0.03 | 0.59 × ($20M / $3.1bn) × ¼ |
| FY27 adj. EBITDA margin (pp) | +0.05 | brief |
| FY27 EPS ($) | +0.01 | brief |
| Stock ($/share) | **+1.5** ($0.6 on the fixed-multiple nights line plus ~$1 for the loss of the memo's "hotels are decelerating" corroboration into the 5 Nov and Feb narratives) | claim 12; judgement |
| **EV = P × impact** | **0.38 × $1.5 ≈ $0.6/share** | |
| Materiality | **Immaterial** (EV under $1/share). The memo can drop the hotel line as a risk; keep the weekly STR series as an alt-data monitor only | |

RESUME: the next agent (audit response) should attack (1) the FY26-implied Q4 arithmetic (quarter weights, the Q2/Q3 assumptions in `r11_path.csv`), which is the anchor; (2) the calendar adjustments (−0.7 election week, −0.2 CR), which are judgement; (3) the base-rate table in claim 10, which is reconstructed from monthly/annual releases rather than an STR quarterly series (if the auditor can reach a quarterly STR table, replace it). Re-run after the August monthly (~25 Sep) and the CoStar/TE November revision.
