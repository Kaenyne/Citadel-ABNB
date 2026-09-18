# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable 5.1, batch A18 with B14 and B16). This question is the lower-tail mirror of R11 (`../risk-q4-us-revpar-strong/`); it reuses R11's distribution (centre +3.5, sd 1.7) and adds an explicit left-tail branch so that P(>= +4) is unchanged at about 0.38 while the tail below +1 is priced from the discrete downside mechanisms. Reproduction: [datasets/b15_model.py](datasets/b15_model.py) (`py -3.13`, numpy/scipy, deterministic, under 1 s; writes `b15_views.csv`, `b15_sensitivity.csv`). Weekly STR series: [datasets/str_weekly_us_3q26_repo_copy.csv](datasets/str_weekly_us_3q26_repo_copy.csv).

## 0. Metadata
- question_name: bonus-q4-us-revpar-soft
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § B15)
- type: binary
- run_mode: initial
- run_date: 2026-09-17
- open_date: 2026-09-17
- close_date: 2027-01-25
- resolution_date: 2027-01-25
- scoring: spot
- cp_visible: no
- cp_value: n/a
- revision: 1
- agent: fable
- batch: A18

## 0b. Question (verbatim)
### Title
Will STR's US hotel RevPAR growth for 4Q26 be <= +1% y/y?
### Resolution Criteria
**Type.** Binary. **Resolution.** As R11 with threshold <= 1.0%. Resolution ~25 Jan 2027.
### Fine Print
None in the registry. Conventions adopted (identical to R11's so the two questions are one object): (1) the resolving series is CoStar/STR's US monthly hotel-performance release (all-US RevPAR y/y); the mean of the October, November and December y/y figures resolves (STR's own Q4 figure governs where both exist); (2) trade-press reprints of the STR release count when costar.com is unreachable; (3) values as published at the January read govern; (4) +1.0% exactly resolves Yes. Coherence: P(<= 1) + P(1 < x < 4) + P(>= 4) = 1 with R11's 0.38.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | R11 (17 Sep, rev 1): centre +3.5%, sd 1.7 (normal), P(>= 4) 0.38, P(<= 1) 0.07, P(<= 0) 0.02; inputs FY26-implied Q4 +3.1, AR(1) path +4.0, calendar adjustments -0.1 (comp +0.8, midterm week -0.7, CR -0.2) | `../risk-q4-us-revpar-strong/research-log.md` claim 9, sections 5-6; `datasets/r11_model.py` there | 2026-09-17 | 2026-09-17 | yes |
| 2 | CoStar/STR weekly, 3Q26: July month RevPAR +8.2% (ADR +5.7%); weeks ending 1 Aug +7.3, 8 Aug +7.2, 15 Aug +6.2 (ADR +3.5), 22 Aug +4.4 (ADR +2.3), 29 Aug +1.7 (ADR +0.6, occupancy +1.1; "slowest since early April"; Sun-Thu +10.9% on demand +6.4%, weekend negative), 5 Sep +16.1 (Labor Day mirror). The clean late-August run rate is about +2 with ADR flat | `datasets/str_weekly_us_3q26_repo_copy.csv` (Lodging/CoStar reprints, URLs inside) | 2026-08-26 to 2026-09-11 | 2026-09-17 | yes |
| 3 | 4Q25 base: October 2025 RevPAR $110.35, -0.9% (occupancy -2.4%, ADR +1.5%); early November +6.2% on the 2024 election-week comp; the 39-day shutdown cost about 1.5m room-nights ("minimal disruption"); two weeks to 29 Nov -0.3%; December declines; FY2025 RevPAR -0.3%, the first annual decline since 2020 | R11 log claim 4 (str.com October 2025 release; hoteldata.com; hoteldive 810212) | 2025-11 to 2026-01-22 | 2026-09-17 | yes |
| 4 | Base rate: post-recovery quarterly US RevPAR y/y (2023Q2-2026Q2, 13 quarters, reconstructed from monthly/annual releases as in R11 claim 10): 3, 1.5, 2, 1, 1, 2, 3, 0, -0.5, -1, 0, 3.8, 5.2; share <= +1: 6/13 = 0.46; within 2024-2025 alone 6/8 = 0.75; 2026 H1 both quarters >= +3.8 | `datasets/b15_model.py`; R11 claim 10 | 2026-09-17 | 2026-09-17 | yes |
| 5 | CoStar/Tourism Economics 10 Aug: FY2026 RevPAR +4.4% (raised from +2.8% on 2 Jun), demand +1.7%, ADR +3.1%; FY2027 +2.1%; supply +0.4%/+0.6%; no quarterly path published | R11 log claim 2; `research/notes/overnight/05_macro-outlook-and-transmission.md` section 4.5 | 2026-08-10 | 2026-09-17 | yes |
| 6 | Operators: Marriott and Hilton FY26 RevPAR 3.0-3.5% (raised), Hyatt 3.5-4.5%, Wyndham 0-1%, Choice 0-1.25% US; H1 near +4 inside a 3.0-3.5 FY implies an operator H2 near +2.5% | R11 log claim 6; `05_macro` section 4.5, 4.8; `data/processed/q3nowcast/G/intra_quarter_commentary.csv` | 2026-07-22 to 2026-09-09 | 2026-09-17 | yes |
| 7 | Downside mechanisms with dates: CR expires 11 Dec 2026 (shutdown risk; the Oct-Nov 2025 shutdown cost about 1.5m room-nights, about 0.4% of a month's US demand); the Fed hiked to 3.75-4.00% on 16 Sep with three more priced; TSA throughput -3.7% y/y in August as airfares ration air travel; Michigan sentiment 55.2; midterms 3 Nov | R11 log claim 7; `05_macro` sections 4.1, 4.4, 4.9; R10 log claim 10 | 2026-09-06 / 2026-09-16 | 2026-09-17 | yes |
| 8 | What a <= +1% quarter needs: 4Q25 RevPAR was about $105 (Oct $110, Nov about $103, Dec about $100, all near flat to -1% y/y); a 4Q26 print at +1% means the Q4 level back at the 2024 level in nominal terms while ADR runs +2 to +3 (CPI lodging +2.8% in July), i.e. occupancy -1 to -2 y/y against a base whose occupancy was already -2.4% in October 2025: a demand contraction of the 2025 kind, not a mere fade of the summer premium (August's weakest clean week was +1.7 with occupancy +1.1) | claims 2, 3; `research/notes/overnight/06_consumer-choice-and-willingness-to-pay.md` section 1.2 | 2026-09-06 | 2026-09-17 | yes |
| 9 | Mixture model (this log): 90% trend N(3.7, 1.6) + 10% shock N(0.8, 1.8) gives P(<= 1) 0.096, P(>= 4) 0.387 (R11 unchanged), P(<= 0) 0.042, mean +3.4; E[RevPAR given <= 1] about -0.2%. The pure R11 normal gives 0.071 | `datasets/b15_views.csv`, `b15_sensitivity.csv` | 2026-09-17 | 2026-09-17 | yes |
| 10 | Readthrough: MAR/HLT RevPAR y/y vs Airbnb nights r 0.88 (post-2022) but decoupled since 2024; the hotel line is corroboration for the memo, not an input to the KPI | R11 log claim 8; `research/notes/2026-09-06_predictive-study.md` section 4 | 2026-09-06 | 2026-09-17 | yes |
| 11 | Brief sensitivities: 1pt of 4Q26 nights = $30M; 1pt of ADR about $30M in Q4; FY27 revenue $158M/pt; FY27 EPS $0.0014 per $M EBITDA; $1.50/share per pt of FY27 nights (fixed multiple), $4.90 joint solve | `docs/pitch-forecasts/00_BRIEF.md` | 2026-09-16 | 2026-09-17 | yes |
| 12 | Recency: no CoStar weekly newer than the week ending 5 Sep (11 Sep reprint) as of 17 Sep 08:40Z; the August monthly is due about 25 Sep; no market on US RevPAR exists (R11 claim 11) | `sources/web_search_log_2026-09-17.md` | 2026-09-11 | 2026-09-17 | no |

Newest load-bearing source: the week-ending-5-Sep STR reprint (11 Sep, 6 days old) against a 130-day window; the week ending 12 Sep publishes on 17-18 Sep (monitoring row 1).

## 2. Query Log
1. [repo] `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md`; skill and format references; R11 log, model and JSON (read in full); R13, R16, B06 logs
2. [repo] `data/processed/q3nowcast/G/str_weekly_us_3q26.csv` (copied); `research/notes/overnight/05_macro-outlook-and-transmission.md` section 4.5 (hotels), 4.1/4.4/4.9 via R11 claim 7
3. [computed] `datasets/b15_model.py` (R11 normal, mixture, base rates, sensitivities)
4. [fetch] lodgingmagazine.com/?s=costar; hotelnewsresource.com front page; hoteldive.com hotel-performance topic (saved; nothing newer than 11 Sep)
5. WebSearch: CoStar U.S. hotel results week ending 12 September 2026 RevPAR (final 72-hour recency check for this question: the week ending 12 Sep is not yet published; nothing new)

WebSearch calls charged to B15: 1 of 5.

## 3. Leading Hypothesis Entities
CoStar, STR, Tourism Economics, US hotel RevPAR, continuing resolution, Federal Reserve, TSA, Marriott, Hilton

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Use R11's normal unchanged (P 0.07) | kept as the anchor and the floor | a symmetric normal has no room for the discrete December shutdown and the airfare/rate-hike demand channel; the 2024-25 record shows <= +1 was the norm only two quarters ago (claim 4) |
| Use the 2023-26 base rate (0.46) or the 2024-25 rate (0.75) | discarded as the point | 2026 is a different regime: H1 +3.8/+5.2, summer +5-8, and the comp is the soft 2025 base itself (claims 2-4); the base rate says only that flat hotel quarters are not exotic |
| Full unwind of the summer premium: late-August clean weeks (+1.7) are the Q4 run rate | kept inside the trend branch's left half | the +1.7 week had occupancy +1.1 and a Labor Day shift; the Sun-Thu +10.9 says business/group demand was firm; October's -0.9 comp adds about +1 |
| A December shutdown (CR 11 Dec) tips Q4 below +1 | kept, inside the shock branch | the 2025 shutdown cost about 1.5m room-nights over 39 days, about 0.4% of a month's demand: it moves December by about -1 to -1.5, and Q4 by about -0.5; alone it does not get a +3 quarter to +1 |
| A consumer recession (Fed hiking into 4.1% unemployment, sentiment 55) | kept, the main shock-branch content | demand -2 to -3 would do it; the probability of that showing inside Oct-Dec stay dates is the 10% weight |
| Hotel RevPAR as a forecaster of ABNB Q4 nights | kept for the impact table at a low slope | claim 10 |

## 5. Independent Estimates
- base_rate_estimate: 0.20 - the 13-quarter post-recovery share of <= +1 quarters (0.46) regime-conditioned by the two-step AR(1) from a +5.5 summer toward a +2 long run (which puts the centre near +3.5 to +4): a weighted 0.4 x 0.46 + 0.6 x 0.07 = 0.22, rounded to 0.20; the honest reading is that "flat hotels" was the 2024-25 norm but 2026's level of demand is a break from it
- decomposition_estimate: 0.096 - the R11 centre and sd carried as the trend branch (90%) plus a 10% shock branch centred at +0.8 (shutdown, rate-hike/airfare demand contraction, summer premium fully unwound), tuned so that P(>= 4) stays at 0.387 (claim 9)
- anchor_estimate: 0.07 - R11's own normal (claim 1); no tradable market on US RevPAR (claim 12)
- anchor_value: 0.07 (R11 distribution, 17 Sep 2026; no market)
- final_estimate: 0.10 (credible interval 0.05-0.18)
- final_minus_anchor: +3 points. NOT_INDEPENDENTLY_DERIVED flag: by design, B15 shares R11's centre and spread; the +3 is the left-skew from the dated shock mechanisms (CR 11 Dec, the 16 Sep hike, TSA -3.7%) that R11's symmetric normal does not carry, and the 2024-25 base rate is what keeps the interval's upper end at 0.18

## 6. Final Numbers
**Binary.** P(STR US RevPAR 4Q26 y/y <= +1.0%) = **0.10**, credible interval **0.05-0.18**.
Joint object with R11: P(>= 4) 0.38, P(1 < x < 4) 0.52, P(<= 1) 0.10; P(<= 0) 0.04; E[RevPAR given <= 1] about -0.2%; mean +3.4.
Extreme-probability gate: not triggered (0.10). The interval's lower end (0.05) is the pure-R11 number.

## 7. Sensitivity
Rows from `datasets/b15_sensitivity.csv` (P(<= 1); P(>= 4) in brackets).
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Shock weight 0.10 | 0.05: 0.07 [0.41]; 0.20: 0.15 [0.35] |
| Shock centre +0.8 | 0.0: 0.11; +1.5: 0.08 |
| Trend centre +3.7 | 3.1 (FY-implied only): 0.14 [0.26]; 4.0 (AR path only): 0.08 [0.45] |
| Trend sd 1.6 | 1.2: 0.07; 2.2: 0.15 |
| December shutdown realised (trend -1.6) | 0.28 [0.11] |
| October monthly prints <= +2 | 0.24 [0.05]; October >= +4: 0.06 [0.63] |
| Joint bear (w 0.2, trend 3.1, shock 0.0) | 0.22 [0.23] |
| Joint bull (w 0.05, trend 4.0) | 0.06 [0.48] |

Pre-mortem ("it is 25 Jan 2027 and Q4 printed <= +1%"): (1) the summer was the World Cup and America 250, and once they lapped, the underlying 2025 no-growth regime (FY25 -0.3%) reasserted itself: August's +1.7 clean week was the tell, not the noise; (2) the Fed's September hike and $100+ oil (Brent $108, R10/B06 context) cut leisure demand into the holidays while airfares rationed air travel (TSA -3.7%); (3) a December shutdown at the CR expiry took 1-1.5 points from December on top of a weak November after the midterms. ("It printed >= +3"): the soft 2025 base (Oct -0.9) and luxury/group strength held the aggregate; the modal path. Asymmetry: a Yes helps the short's narrative (hotels confirming a US demand rollover) but does little to Airbnb's own KPI (claim 10); the cost of a wrong Yes is only credibility.

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| weekly (Thu/Fri) | CoStar weekly US results (Lodging reprint); first the week ending 12 Sep | September clean weeks <= +2: +0.03 each fortnight of confirmation; >= +5: -0.02 |
| 2026-09-25 (approx.) | CoStar August 2026 monthly | August <= +4: +0.02; >= +6: -0.02 |
| 2026-10-02 | Prelim memo freeze | quote 0.10 (0.05-0.18) with R11's 0.38 as one object |
| 2026-10-21 to 2026-11-03 | Hilton, Hyatt, Marriott Q3 prints and FY26 RevPAR guides | a cut in FY guides or a Q4 "flat" call: +0.05; a second raise: -0.03 |
| 2026-11-03 | Midterms | no action; priced |
| 2026-11-10 (approx.) | CoStar/TE November forecast revision | each -0.4pp on FY26: +0.04 |
| 2026-11-20 (approx.) | CoStar October monthly | October <= +2: move to about 0.24; >= +4: about 0.06 |
| 2026-12-11 | CR expiry | a shutdown: move to about 0.28 |
| 2026-12-20 (approx.) | CoStar November monthly | update the three-month mean arithmetic |
| 2027-01-22 (approx.) | CoStar December monthly / FY2026 release | resolve on the mean of the three months |

## 9. Impact
If Yes (E[4Q26 RevPAR given <= 1] about -0.2% vs the base-case +3.4%: -3.6pp of US hotel RevPAR, a stay-date, US-only series that has decoupled from Airbnb's KPI since 2024):

| Item | Delta if B15 happens | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | 0 | Q4 series; Q3 resolves first |
| 4Q26 nights (pts) | **-0.7** (RevPAR-to-nights slope about 0.4 on the 2023-26 co-movement x 3.6pp, halved for the stay-date/bookings mismatch and NA's about 30% share of nights) | claim 10; R11 section 9 (mirror of its +0.4 for +1.7pp) |
| ADR (pts) | **-0.5** (NA ADR co-moves with hotel ADR direction; the pricing residual does not) | claim 10 |
| 4Q26 revenue ($M) | **-36** (0.7 x $30M + 0.5 x about $30M) | claim 11 |
| FY27 revenue ($M) | **-60** (a weaker Q4 booking base carries into 1Q27 recognised revenue; about 0.4pt of FY27 growth) | kernel carry; claim 11 |
| FY26 adj. EBITDA margin (pp) | -0.05 (0.59 x $36M / $12.9bn x the Q4 weight) | brief |
| FY27 adj. EBITDA margin (pp) | -0.10 (0.66 x 0.4pt / about 2.7) | brief |
| FY27 EPS ($) | -0.04 ($60M x 0.66 x $0.0014, rounded) | brief |
| Stock ($/share) | **-2.5** (-$1.0 on the fixed-multiple nights line, about -$1.5 for the corroboration a rolling-over US hotel tape gives the memo's deceleration narrative into the Feb print; the joint-solve line would say -$3.4 on nights alone) | claim 11; R11 section 9 |
| **EV = P x impact** | **0.10 x -$2.5 = -$0.25/share** | |
| Materiality | **Immaterial** (EV under $1/share). The memo can carry the hotel tape as a monitor and, if October prints <= +2, as a one-line corroboration; it is not a bonus item worth a number | |

RESUME: the next agent (audit response) should attack (1) the 10% shock weight and its +0.8 centre (claim 9), which are judgement; a December shutdown probability from a Kalshi/Polymarket government-shutdown market would tighten it; (2) the base-rate table (claim 4), reconstructed from monthly releases; (3) the conditional mean given Yes used in the impact table. Re-run after the week-ending-12-Sep weekly, the August monthly (about 25 Sep) and the October monthly (about 20 Nov); keep B15 and R11 on one distribution.
