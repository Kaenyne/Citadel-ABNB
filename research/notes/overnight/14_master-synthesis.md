# 14. Master synthesis of the overnight run, 6-7 September 2026

**What this is.** One document that reconciles workstreams 01-13 and the red-team pass (15) into a
single answer: what our data predicts, what it does not, what the model now says, what to expect on
5 November, and what the pitch can and cannot claim. Written for Krish on waking.

**Compiled:** 7 Sep 2026. Price used throughout: **$181.94** (4 Sep 2026 close). Balance sheet 30 Jun 2026.
Q3 2026 prints **5 Nov 2026**; pitch ~Dec 2026.

**Sources read in full:** `research/notes/overnight/01_*` through `13_*` and `15_red-team.md`;
`research/notes/2026-09-06_predictive-study.md`; `research/notes/2026-09-05_driver-model.md`;
`docs/2026-09-05_plan-of-attack.md`; `research/thesis.md`; `model/assumptions.md`;
`docs/overnight/RUN_STATE.md`.

**Corrections policy applied here.** Every one of WS15's 20 numbered corrections and 16 cross-note
conflict rulings has been applied or explicitly overridden below, and section 10 lists them. Where
WS13's "Choices made" already resolved a conflict, **WS13 wins**, because the model — the thing the
pitch will actually run on — is built on those choices. The two places that matters are FY27 revenue
growth (**+11.3%**, WS13's build, not WS15's +12.3% arbitration) and the FY27 margin (**35.9%**,
WS13's lever stack after the AI referral cost, not WS07's 36.6% before it).

---

## 0. The single most important thing in this document

**The base-case price fell from $248 (5 Sep) to $181 (7 Sep), and $55 of that $67 is the exit
multiple.** Not the operating case. The rest moved $12 in total: -$5 of EBITDA, -$4 of net cash (an
actual correction — the old path never subtracted RSU tax withholding, ~$0.7bn a year) and -$3 of share
count (**WS18's fix to the FY2026 roll-forward, which had double-counted the 1H26 buyback**; see the
post-run corrections section at the end of this note).

WS12 triangulated the FY27 exit multiple three independent ways — a 2023-26 time series of ABNB's own
multiple against forward growth, a 19-name cross-section, and a fade DCF — and **all three land below
the 18 / 22 / 25.5x the 5 Sep model assumed.** The recommended set is **13.5 / 16.5 / 18.5x**. The
highest live sell-side target on the tape ($220, Rosenblatt / DA Davidson) implies **19.3x**; the mean
target ($178.96 across 46 analysts) implies **15.4x**. Nothing published anywhere supports 22x, let
alone 25.5x.

At WS13's model, WS12's multiples and a 25/50/25 weighting, the EV/EBITDA lens is worth **$176**
(-3.2% vs spot). On the full football-field means it is **$157** (-14%). On the old multiples it is
**$231** (+27%). *The entire difference between "ABNB is a buy" and "ABNB is fairly valued" in our own
work is the exit multiple, and we now have three methods saying the low number is the right one.*

**So the pitch has exactly three honest routes to upside, and it must pick one and argue it explicitly:**

1. **FY27 revenue above ~$16.0bn** (we model $15.84bn; the Street $15.73-15.76bn). Growth is the only
   fundamental that has ever moved this multiple: **+0.48 turns of EV/EBITDA per point of NTM revenue
   growth** (t 8.3 levels, +0.49 t 5.6 in 12-month changes). Margin moves it **zero** (t 0.3).
2. **SBC below ~10% of revenue** (it is 12.9%). ABNB's premium to peers on EBITDA and revenue is
   *entirely* the SBC add-back: on EV/NTM SBC-adjusted FCF it trades at 27.3x against a peer median of
   27.2x. Once SBC is charged, the market pays ABNB nothing for being ABNB.
3. **A separately named, separately sized optionality bucket** (hotels, Experiences, Services, ads),
   priced as its own line rather than smuggled into the core multiple. WS11 sizes the genuinely
   incremental FY28 contribution at **$235m / $914m / $1,987m = 1.4% / 5.4% / 11.7%** of revenue.

Anything else is an argument that the market should pay a multiple it has never paid on this growth rate.

---

## 1. One-page answer: what predicts what

### (a) KPIs (nights, ADR, GBV)

| Target | What forecasts it | Strength | What does not |
|---|---|---|---|
| **ADR, the FX component** | The dollar. `ADR FX (pp) = 0.52 − 0.715 × broad USD y/y` (n 17, r −0.96) or `−0.61 + 0.460 × EUR/USD y/y` (n 17, r +0.99). Daily, real-time, **walk-forward RMSE 0.44x naive / 0.41x AR(1)**, sign right 8 of 10 | **Strong and mechanical.** The only genuine out-of-sample forecast the team owns | Nothing else. It is an accounting identity with a lag |
| **ADR, ex-FX** | Nothing forecasts it. Three medium-confidence coincident correlates agree (initial claims r −0.78, airline-fare CPI +0.70, jet fuel +0.70, all n 14) and all three currently nowcast **+3.6% to +4.1%** for 3Q26 | Watch-list only; the target is integer-rounded in the letters | Hotel prices (the gap closed in 2026), Inside Airbnb like-for-like price (r +0.13 with ADR, n 8, and the source stopped publishing prices) |
| **Nights** | **Nothing.** 1,408 macro pairs (WS05) → zero high-confidence, one medium and it is coincident. 598 alt-data pairs (WS08) → nothing beats AR(1) on both evaluation windows. 3,446 regional benchmark correlations (WS10) → the strongest LatAm result is r +0.95 with *French* Eurostat platform nights, which is the calibration for what a single high r is worth | **Nil.** Michigan sentiment vs nights: **r −0.05** | Google Trends (432 tests, 0 of 162 beat naive on the full window; ABNB's share of search fell 5.7 pts over two years while nights growth *rose*), Eurostat (150-day lag, lead correlation −0.11), Inside Airbnb (fixed-13-city panel has n = 0 usable quarters), hotel RevPAR and BEA (2023-trend artefacts: r falls 0.88 → 0.45 and 0.88 → 0.33 when 2023 is dropped) |
| **Nights, coincident sanity checks that do work** | **BKNG room-night acceleration** → total nights r **+0.91**, EMEA r **+0.88** (n 7, acceleration basis), and BKNG prints ~8 days before ABNB. **StatCan Canadian returns from the US** → NA nights r +0.72 (n 15) | Usable as a directional check, not a model | Japan (JNTO) inbound arrivals: decoupled, r −0.12. ABNB's APAC growth is origin and domestic |
| **GBV** | Nothing independent. It is nights × ADR | — | The one macro hit (real PCE) flips sign across windows |

### (b) Income-statement items

| Line | What forecasts it | Strength |
|---|---|---|
| **Revenue** | **The guide midpoint plus the trailing cushion.** MAE **1.1%**; ABNB has beaten its own midpoint **19 of 19** times, finished above the *top* of the range **15 of 19**, and never below the bottom. Nothing we built beats it | Strong, and boring. It is the house forecast |
| **Revenue, FX component** | `revenue FX (pp) = −0.640 + 0.413 × mean(EUR/USD y/y at t−1, t−2)` (n 17, r +0.80). Revenue is recognised at check-in, so it lags spot 1-2 quarters. Validated out of sample against management's guided +3.0pp for 3Q26: the lagged fit says **+2.2pp**; the contemporaneous fit, which has the *higher* in-sample r, says **−1.6pp** | **New tonight and load-bearing.** ±0.8pp error band |
| **Adj. EBITDA margin** | A nowcast, not a forecast. Prior-year same-quarter margin + ADR ex-FX + S&M deleverage has LOO error **2.0 pts** vs 2.8 for the guide bound — but the gain is all the S&M term, which needs the print's own S&M. With lagged inputs only it ties the guide. FY floors have been beaten **4 of 4** by 60-140bps | Medium. Use the floor + cushion |
| **Backlog → revenue** | Funds held for clients (prior quarter end) → next-quarter revenue: r +0.89, walk-forward **0.60x naive / 0.59x AR(1)** on the 2023Q1 window (n 10)… **but 1.69x / 1.85x on the 2022Q1 window in the same file (n 14).** WS08 reported only the favourable window | **Do not use it as a validated forecaster.** If it is used at all it must be used with both numbers (WS15, CONF-07) |
| **SBC, tax, take rate** | Management's own guides are the worst on these lines: FY24 SBC guided +20% then +25%, delivered **+30.8%**; FY25 take rate guided +20bps, delivered **−16bps** (a 36bp miss on the most model-relevant number given in 2025) | Haircut expense guides; treat take-rate guides as directional only |

### (c) Guidance

- **How management guides:** one quarter ahead on revenue $ (a range), take rate, GBV and nights (buckets),
  and margin (a ceiling); one year ahead on FY margin (a floor, since 4Q23) and FY revenue growth (a floor,
  since 4Q25). Numeric guides per print went from 0-1 (2020-21) to **8-10** (2024-26). Two-quarter-ahead
  guides exist but are rare and only 2 of 3 verified.
- **Accuracy:** 159 scored guides. Ranges 28 of 39 beaten above the top, **0 below**. Floors 35 of 36 met.
  Ceilings 12 of 14 met. Directional 35 of 43. Point estimates are the weak ones (3 of 22 at the point) and
  **every point-guide miss is an expense or monetisation line**.
- **Cushion:** mean beat vs midpoint **+2.54%**, median +2.52% over 19 prints; over the last 8 prints
  **+1.86% mean / +1.79% median**. The range itself narrowed from 4.9% of the midpoint to **1.90%**.
  *The company sandbags less than it used to, but it still sandbags.*
- **The FY guide has only ever been raised, never cut**, and in 2024 and 2025 the raise landed at the
  **Q3 print**.
- **What the market punishes:** not the beat. Revenue beat vs guide has a **0.37 sign hit rate** against
  the day-1 excess return — worse than a coin flip. Beat vs *consensus* is barely better (positive at 22
  of 23 prints, so the event carries no information). Across WS02's 17 tests, WS04's 97 tests and WS03's
  948 tests, **not one day-1 specification has a positive leave-one-out R².**

### (d) The stock

| Claim | Evidence | Verdict |
|---|---|---|
| Nights **acceleration sign** sets the day-1 reaction | 17 of 21 (predictive study); post-2022 accelerating prints +6.7% day-1 (n 5) vs decelerating −5.4% (n 9); WS04's independent sign test 7 of 9 positive, p 0.070 vs the base rate. **As a regression it fails: R² 0.032, LOO R² −0.18** | **A base rate with its n, not a model.** Standardise the definition before 5 Nov — WS01, WS04 and WS05 count "acceleration" three different ways (CONF-16) |
| Nights vs the **StreetAccount nights consensus** drives the 20-day drift | n 18, R² 0.220, slope **+1.54 pts of 20-day excess per 1% nights beat**, HC1 t 2.46, perm p 0.053, **LOO R² +0.13**. Post-2022 (n 11): R² 0.373, slope +2.83, crosses zero at a **+1.83% nights beat**. Median nights beat in the sample is +0.58%, so the *typical* print is followed by a negative 20-day excess | The best out-of-sample reaction result in the run — but it is one of **nine** positive-LOO specs among 75, not "the only one" (WS15 correction #7). Needs two clean confirmations before it is pitchable |
| **Guide below Street** is a risk flag | All **9** such prints had a negative 20-day excess (mean **−8.90%**); p 0.002 vs a coin flip and **p 0.057 vs ABNB's actual 72.7% base rate of negative 20-day excess**. Report the base-rate version. The ninth is 2Q24, whose −3.65% guide-vs-Street was recovered by WS16 (Reuters, 6 Aug 2024: Street $3.84bn vs a $3.70bn midpoint). Day-1 the two groups now separate at Mann-Whitney p 0.040, gap 5.5pts | Usable as a binary flag. **Live for 5 Nov**: Zacks Q4-26 revenue is $3,200m = +15.2% y/y against an expected +11-13% guide |
| **Post-print drift** is negative and lives in the up-prints | 20 sessions after the reaction day: all prints −3.7% (t −2.16, p 0.042, negative 15 of 23); day-1-up prints **−7.1%** at 20d and **−14.8%** at 60d (negative 8 of 10); day-1-down prints −0.7% / +0.4%, i.e. zero. **Pops fade, drops do not bounce** | Real but regime-broken: from 2023 the all-print drift is −2.3% (not significant) and the last three up-prints drifted −1.4%, **+5.5%, +3.2%** |
| Print days are **re-ratings, not estimate changes** | Across 2023-26 prints the day-1 move correlates **+0.97** with the change in the EV/NTM-revenue multiple and **+0.09** with the change in the estimate. On the nine moves ≥7%, 84% of the absolute move is multiple. 2Q26 was +17.4% on an estimate change of **−0.2%** | The most important single fact about how this stock trades |
| **Management language** | Long-term-target / full-year framing share of prepared remarks: detrended r **+0.69** with day-1 (perm p 0.0005), +0.72 controlling for the numbers. Classic sentiment is worthless: LM net tone r **+0.08**. **948 tests, zero survive Benjamini-Hochberg at q<0.10**; best q 0.12 | Knowable only at ~17:30 ET on print day, after the letter and after the after-hours move. **Explanatory only. There is no version of this that becomes a forecast.** Put it in the pre-call checklist, never in a model |
| Beta, rates, seasonality | Beta to the 10-year yield is **statistically zero in every year since 2021** (|t| ≤ 0.9) — ABNB never had a rates beta, it had a long-duration-growth beta and it has fallen 1.28 → 0.91. 64% of 2026 daily variance is idiosyncratic; **+32.7 of the +34.0 pts of 2026 return is stock-specific alpha**. May: negative vs QQQ **6 of 6**, −14.5%. November: negative **5 of 5**, −5.1% | Seasonals are base rates found among 54 tests; do not trade them, do put November on the calendar |

### The five things that are new tonight

1. **The exit multiple is the whole pitch (WS12).** Three independent methods, all below the assumed set;
   $55 of the $64 fall in the base-case price. *This reframes the entire deck.*
2. **Revenue FX lags spot by one to two quarters, and the 4Q26 number is already 84% determined (WS05).**
   Revenue FX goes from ~+3.0pp in 3Q26 to **−0.4pp in 4Q26 under all three dollar paths**. That is a
   **3.4pp mechanical cut to reported revenue growth with no change in demand.** The 5-6 Sep work treated
   FX as contemporaneous and could not model this; the 5 Sep note explicitly flagged the gap it could not
   close. Have the bridge ready *before* the Q4 guide, not after.
3. **Roughly half of ADR growth is bedroom mix, not price (WS06).** 2Q26 is the first quarter Airbnb
   published Bedroom Nights Booked: **+12% against nights +10%**, with LTM bedroom nights past 1 billion.
   That implies **≥1.786 bedrooms per booked night** and **≤$102.87 per bedroom-night** against a US hotel
   ADR of $171.74. Airbnb is not out-pricing hotels; it is selling a bigger unit. The corollary is a
   warning: **ADR is more cyclical than it looks, because size mix is discretionary.**
4. **Consensus now exists for all 23 prints (WS04), and it closes the biggest hole in the census.**
   Theo's `consensus_snapshots.csv` was 23 rows of "missing". We now have revenue at 23/23, next-quarter
   revenue 18/23, nights 18, EPS 17, GBV 12, EBITDA 8, with 145 verbatim sourced quotes. It produced the
   one 20-day result above and it kills "beat vs consensus" as a day-1 story for the third independent time.
5. **The 2026 marketing ramp is media, not headcount — the opposite of 2025 (WS07), and the AI cost is
   already visible on the balance sheet.** FY2025 S&M growth was field operations +43% with brand and
   performance +10%; **1H26 is brand and performance +32% against field ops +24%**. Media spend is
   discretionary and reversible; field-ops headcount is not. Separately, non-cancelable purchase obligations
   went **$719M → $1,749M** and the data-hosting commitment from "$672M through 2027" to "**$1.7bn through
   2031**" — which settles the Chesky ("AI will not affect the P&L") vs Mertz ("a material increase in AI
   spend") dispute in Mertz's favour, from the primary filing.

**And the strongest single result of the night is a negative.** 598 alt-data tests (WS08), 1,408 macro
pairs (WS05), 3,446 regional benchmark correlations (WS10), 948 language tests (WS03), 218 stock tests
(WS09), 97 reaction tests (WS04), 77 valuation tests (WS12). **Nothing in the alt-data layer beats AR(1)
on both evaluation windows**, and every apparent winner is either the mechanical FX pair, not knowable
before the print, or window-dependent. Three composite demand/supply/price indexes all lose to "same as
last quarter". That is a stronger answer in a Q&A than a fabricated edge.

---

## 2. Data-to-KPI map

**Bottom line: 217 datasets, 5 with a surviving out-of-sample signal, and 4 of the 5 are the same FX
mechanism or the guide itself.**

### 2.1 Dataset family → target → verdict

| Family (WS01 ids) | Rows | Primary target | Verdict after tonight |
|---|---|---|---|
| **FX (FRED daily)** D087/D088/D241/D269 | 9 | ADR FX effect; revenue FX | **WORKS.** ADR: WF 0.44x naive, 8/10 signs. Revenue: lagged 1-2q, validated against the guided +3.0pp. Use slope **−0.715 per pt of broad USD** everywhere (WS15 #4; the −0.59 n=14 fit is the alternative) |
| **Guide + trailing cushion** D005/D037/D038 | 3 | Revenue | **WORKS.** MAE 1.1%, 19/19. The house forecast |
| **Nights acceleration sign** D001/D042/D247 | 3 | Day-1 reaction | **BASE RATE ONLY.** 17/21 in the predictive study; R² 0.032 / LOO −0.18 on tonight's `04_reaction_tests.csv` (WS15 #3) |
| **Consensus at print** (new, WS04) | 23 prints | 20-day excess | **ONE SURVIVOR:** nights vs Street nights, LOO +0.13 at 20 days. Nothing at day 1 |
| **Prior-quarter S&M deleverage** D009 | 1 | Day-1 excess | r +0.59, n 17, one hit in ~60 tests, sign not pre-specified. **Pre-register for 5 Nov or drop** |
| **XBRL backlog** (funds held, unearned fees) D015/D259 | 21→42 cells | Next-quarter revenue | **WINDOW-DEPENDENT.** 0.59x AR(1) on 2023Q1+ (n 10); **1.85x AR(1) on 2022Q1+ (n 14)**. Unearned fees are dead (−0.9% y/y vs revenue +16.5%; RNPL broke it) |
| **Google Trends** (9 terms × 2 geos) | 432 tests | Nights, GBV, revenue | **DEAD.** 0 of 162 beat naive on the full window; 7 of 162 post-2022, none by >17%. Google renormalises history on every pull, so nothing here is point-in-time |
| **Eurostat platform nights** D110-D115 | 64 tests | EMEA nights, revenue | **CATEGORY CHECK, NOT A NOWCAST.** Best knowable feature 1.09x naive; lead correlation −0.11; **stops at March 2026** (150-day lag), so 2Q26 will still be incomplete on 5 Nov. Value: EU27 platform nights +9.7% (1Q26) vs total EU nights +1.7% in H1 — share gain in a low-growth market |
| **Inside Airbnb (13-city, 168 dumps)** D120-D131 | 36 tests | Nights, ADR, supply | **NO TEST YET.** Fixed-13-city panel has **n = 0** usable year-ago quarters (1 city in 2023Q4-2024Q4, 13 only from 2026Q3). Listings y/y is a supply/regulation series and forecasts nights **3.6x worse than naive**. `reviews_l30d` on matched ids is the metric to capture monthly (6/7 signs, 0.81x) |
| **Common Crawl** D150-D155 | 5 | Supply quality | Survival appears in the beat-naive list at 0.69x but with the **wrong sign** (better survival, slower nights). Discard as a demand series; keep as professionalisation evidence. **No prices exist in CC, in any era** |
| **Macro (28 FRED series)** D070-D101 | 1,408 pairs | Nights, ADR, margin | 3 high-confidence, all the same FX mechanism. 16 medium, all coincident. **Nights column empty on purpose** |
| **Peer prints** D060-D062 | 24 event tests + benchmarks | Nights (coincident), stock | BKNG room-night **acceleration** r +0.91 total / +0.88 EMEA (n 7) and it prints 8 days early — a usable directional check. **No tradeable read-across**: peer print event studies give 2 nominal hits in 24 tests with contradictory signs |
| **Transcripts / language** D050-D057, WS03 | 948 tests | Day-1 reaction | Explanatory only, and nothing survives BH. Credibility scorecard is the usable output |
| **Regulatory database** D160-D171, WS11 | Monte Carlo | Revenue, EMEA nights | Median drag 0.15% / 0.45% / 0.87% of revenue (2026/27/28); mean 0.25 / 0.75 / 1.23; **p95 0.92 / 2.74 / 3.96**. 93% European. **No European regulatory event has ever moved this stock** (WS09 event studies) |
| **Valuation / peers** D282-D288, WS12 | 77 tests | The multiple | **Forward revenue growth is the only fundamental that moves it: +0.48 turns per point.** Margin: zero |
| **Options ledger, short interest, analyst actions** D044/D267/D268 | 60+ tests | Positioning | Nothing predictive. SI 2.17% (3-year low, no squeeze). Analyst actions are a print echo: PT raises +2.9% same-day across 206 events, **−0.2% (p 0.25) once print weeks are removed** |

### 2.2 Composite indexes — all three fail (WS08)

| Index | Target | WF n | ratio vs naive | vs AR(1) | Verdict |
|---|---|---|---|---|---|
| Demand (7 components, equal-weight z) | nights | 10 | **1.66** | 1.58 | worse than doing nothing |
| Demand, NNLS refit each quarter | nights | 12 | 1.40 | 0.98 | no |
| Demand | GBV / revenue | 10 | 1.28 / 1.28 | 1.13 / 1.26 | no |
| Demand, z-baseline restarted 2023Q1 | nights / revenue | 7 | **0.78 / 0.81** | 0.99 / 0.80 | ties AR(1) on 7 quarters, r with nights +0.25. **Recorded, not recommended** |
| Supply (2 components) | nights / ADR | 5 | 1.19 / 1.44 | 0.91 / 1.19 | no |
| Price (3 components) | ADR / ADR ex-FX | 10 | 1.09 / 1.40 | 0.88 / 1.11 | **beaten by one of its own components** |
| **FX contribution alone** | ADR FX / ADR | 10 | **0.44 / 0.64** | 0.41 / 0.51 | the only thing that works |
| Funds held alone | revenue | 10 | 0.60 | 0.59 | window-dependent (see 2.1) |

**Diagnosis, and it is worth a slide.** Every component's expanding z-score is anchored on 2021-22
reopening levels, so from 2024Q3 to 2026Q2 all of them sit between −0.3 and −1.2 and the index barely
moves. Aggregation *dilutes*: adding CPI lodging, BEA hotel prices and Inside Airbnb prices to the FX
term takes the Price index from 0.64 to 1.09. The NNLS version confirms it by putting weight 1.57 on FX
and zero on almost everything else.

### 2.3 The gaps — where the model has to assume rather than measure

Occupancy (nothing in the repo measures it; the booking-curve file is a *blocked-night rate*).
Quarterly ADR ex-FX before 4Q25 (only three quarters are letter-stated). RNPL share of GBV beyond
">20%". Segment revenue for hotels, Experiences and Services (none disclosed, ever). The brand-vs-field
S&M split before 2023. Headcount and SBC per employee. **Cross-border share of gross nights, urban share,
long-term-stay share and active-listing growth — all stopped in 1Q24, and all four were decelerating when
they stopped.** Host earnings, stopped after 2023, exactly as the take-rate migration began. That
disclosure pattern is itself a pitch point.

---

## 3. Guidance: how it works, and what the market actually punishes

**Bottom line: the guide is the best revenue forecast anyone has and it carries no information about the
stock. Model with it; do not trade on it.**

### 3.1 The mechanics

- **Horizon.** One quarter on revenue $, take rate, GBV/nights buckets and the margin ceiling. The full
  year on margin (a floor, since 4Q23, reiterated verbatim in May and August and **converted to a point
  estimate at the Q3 print** in both 2024 and 2025) and on revenue growth (a floor, new in 4Q25). No FY27
  guide will be given on 5 November — management has never given one in November.
- **The revenue range is a floor dressed as a forecast.** 15 of 19 above the top, 0 below the bottom.
- **Cushion trend:** +3.04% over the first 11 prints → **+1.86% over the last 8**, with the range width
  down from 4.9% to 1.9% of the midpoint. Use the trailing-8 cushion (~1.8%), not the full history.
- **Bucketed nights and GBV guides are the most beatable line in the letter** — 5 of 5 above the bucket,
  by **+1.2 to +4.8 pts** (WS15 correction #5; the note's original "+3 to +5" was contradicted by its own
  cited 1Q26 instance of +1.2).
- **Guides that go wrong are expense and monetisation lines, and 5 of the 7 wrong directional guides were
  wrong in the company's favour.** The two that were not: the FY25 take-rate guide (+20bps guided,
  −16bps delivered) and the 1Q24 promise that 3Q24 growth would accelerate (it decelerated).

### 3.2 Management credibility, by horizon and by person (WS03, 66 closed claims)

| Cut | Hit rate |
|---|---|
| Next quarter | **80%** (n 15) |
| Full year | 73% (n 30) |
| **Multi-year** | **26%** (n 19) |
| Quantified | **82%** (n 27) |
| Unquantified | 49% (n 39) |
| Prepared remarks / letter | 100% / 75% |
| Unscripted Q&A | 52% |
| Dave Stephenson (CFO to Feb 2024) | 74% |
| Ellie Mertz (CFO from Mar 2024) | 63% |
| **Brian Chesky** | **42%** |
| **Pricing / ADR / affordability** | **0 of 7** |

**How to use it:** take next-quarter and full-year quantified guidance as ~80% reliable and
directionally conservative; discount anything the CEO says about ADR, affordability, market penetration
or the size of a new business to roughly a coin flip; apply a haircut to any multi-year or unquantified
assertion carried into the DCF (realisation 26% and 49%).

**The dropped claims matter for the Services/Experiences bull case.** Chesky, 3Q24: *"Every year now, for
the coming years, we will launch one to two new businesses that will generate $1 billion or more of
revenue incrementally a year."* Twelve months later, 3Q25: *"it's going to take three to five years… for
services, experiences to become a material part of our business."* Never repeated, never withdrawn. That
$1bn-a-year cadence is the number the Services bull case was built on.

### 3.3 The reaction function as now understood

Five candidate variables, ranked by what actually survives:

| Variable | Horizon | Status |
|---|---|---|
| **Change in the EV/NTM-revenue multiple** | day 1 | corr **+0.97** with the day-1 move (2023-26). This is a description, not a predictor — but it tells you the print is a positioning event |
| **Nights vs Street nights** | 20 days | slope +1.54 pts per 1% beat, LOO **+0.13**; crosses zero at a +1.83% beat post-2022. **The only defensible out-of-sample reaction result** |
| **Nights acceleration sign** | day 1 | base rate: 17/21 (predictive study), 7/9 (WS04), post-2022 +6.7% vs −5.4% (WS05). Fails as a regression. **Quote it with its n; do not put a coefficient on it** |
| **Guide midpoint below next-quarter Street** | 20 days | **9 of 9** negative, base-rate p **0.057**. A binary risk flag |
| Revenue beat vs guide | day 1 | **0.37 sign hit rate.** A bigger beat is, if anything, associated with a *worse* day |
| Consensus revenue surprise | day 1 | R² 0.097, LOO −0.17 |
| Margin guide direction, FY guide action, cushion-aware guide surprise | day 1 and 20 | all LOO-negative (WS02, 17 tests) |
| Long-term-target share of prepared remarks | day 1 | r +0.69 detrended, but knowable only after the close and **fails BH among 948 tests**. Reading guide only |

**The synthesis of all three independent efforts (5 Sep driver model, the predictive study, WS02/03/04):
the print's numbers do not set the print-day move.** The market prices the guide immediately, prices
nights slowly, and re-rates on positioning and forward language. That is why WS13 deliberately put **no
reaction equation in the workbook** — the `Card_5Nov` sheet carries base rates instead. Putting an R²-0.04
regression in an Excel model would be dressing a negative result as a feature.

---

## 4. The model: FY26-FY28 base / bear / bull

**Bottom line: $15.8bn of FY27 revenue at a 35.9% adjusted EBITDA margin, worth about $181 a share on
WS12's multiples against a $181.94 spot. The stock is priced roughly at the base case on reported cash
flow and above the bull case on cash flow after SBC. That gap is the whole debate and two days of work
did not move it.**

`model/ABNB_driver_model.xlsx` — 9 sheets, 2,349 live formulas, 216 outputs reconciling to the Python
mirror to 1e-6 and, after WS17's Excel 16.0 rebuild, to 4.2e-15 against real Excel. Rebuild with `py -3.13 analysis/src/overnight/13_driver_model.py`.

### 4.1 The base case

| Base | FY2026E | FY2027E | FY2028E |
|---|---|---|---|
| Nights & seats booked (M) | 585.7 (+9.9%) | 637.6 (+8.9%) | 685.0 (+7.4%) |
| ADR ($) | 180.32 (+5.3%) | 185.18 (+2.7%) | 189.81 (+2.5%) |
| GBV ($M) | 105,614 (+15.7%) | 118,081 (+11.8%) | 130,026 (+10.1%) |
| Take rate, implied reported | 13.45% | 13.25% | 13.42% |
| **Revenue ($M)** | **14,233 (+16.3%)** | **15,842 (+11.3%)** | **17,944 (+13.3%)** |
| **Adj. EBITDA ($M) / margin** | **5,158 / 36.2%** | **5,686 / 35.9%** | **6,701 / 37.3%** |
| SBC ($M) / % revenue | 1,787 / 12.6% | 1,965 / 12.4% | 2,122 / 11.8% |
| Net income / EPS | 3,065 / $5.20 | 3,258 / $5.67 | 3,906 / $6.96 |
| **FCF ($M) / margin** | **5,129 / 36.0%** | **5,420 / 34.2%** | **6,197 / 34.5%** |
| SBC-adjusted FCF ($M) | 3,342 | 3,455 | 4,075 |
| Diluted shares (M) | 588.9 | 574.6 | 561.5 |
| **FCF / share** | **$8.71** | **$9.43** | **$11.04** |
| **SBC-adj. FCF / share** | **$5.68** | **$6.01** | **$7.26** |
| Net cash ex float ($M) | 9,383 | 10,116 | 11,570 |

Bear FY27 revenue **$14,181m (+1.8%)** at a **28.4%** margin; bull **$17,421m (+19.9%)** at **38.0%**
(41.7% uncapped, cut to WS07's stated realistic ceiling — *a bull that needs a 46% FY28 margin is not a
bull, it is a broken model*).

### 4.2 The driver tree

**Revenue = Σ(regional nights) × ADR ex-FX × (1 + ADR FX) × take rate × (1 + FX timing wedge) + new business.**

- **Nights (WS10, net of WS11).** Four regional growth rates, weighted on **base-period** nights shares
  (NA 29.3 / EMEA 39.6 / LatAm 14.8 / APAC 16.2 at 2Q26), less a regional regulatory drag. FY27 base
  **+8.9%** (WS10 publishes +9.2% gross on its own forward weighting). WS10's panel reconciles to reported
  total nights within **1.1pp in every quarter since 4Q22**, mean residual −0.41pp, which is what makes a
  bottom-up build usable at all. In 2Q26, **LatAm and APAC at 31% of nights delivered 52% of the growth.**
- **ADR ex-FX (WS06 + WS07): +2.5% FY27**, against WS10's +3.0%. Two workstreams against one, and WS06
  shows the bedroom-mix half decaying while hotel pricing decelerates to +1.6% in 2027 (CoStar).
- **FX (WS05).** Two effects, different sizes, and this is the biggest mechanical change vs 5 Sep.
  ADR FX is contemporaneous; revenue FX lags 1-2 quarters. The model carries an explicit
  **FX timing wedge = (1 + revenue FX)/(1 + ADR FX) − 1**: +2.2pp in 3Q26, −0.1pp in 4Q26, ~−0.8pp
  through 2027. *This is why the model reports two take rates* — an assumed 13.37% and an implied
  reported 13.25% in FY27. **The 20bp swing is FX timing, not monetisation.**
- **Take rate (WS06, WS11).** Flat. Single 15.5% host fee is worth **+40 to +50bps gross if the replaced
  blended guest fee was 14.1%, and the sign flips negative above ~14.6%** — management's "modest upside"
  language implies the low end. 2026 already spent it on RNPL timing and new-business incentives.
- **Margins (WS07).** Cost lines driven by their natural unit. FY27 **35.9% after the AI referral cost,
  36.3% before** — between WS07's 36.6% and WS05's 36.4%.
- **Overlays (WS11).** Regulation as a regional nights drag at WS11's mean. AI referral cost at WS11's low
  case in the base (0.38% of FY27 revenue), high in the bear (2.28%), zero in the bull. New business adds
  **ads and Services only** ($197m incremental FY27) — hotels and Experiences are already inside "nights
  and seats booked" and would be double-counted.
- **Valuation (WS12 + WS09).** Exit 13.5 / 16.5 / 18.5x on FY27E EBITDA; cost of equity **10.5%**
  (WS09's low end; WS09 estimated beta across several windows and factor models, 1.16-1.32, and is the
  more thorough estimate than WS12's single vendor figure).

### 4.3 The margin levers (WS07)

The single most important sensitivity in the model **is not a cost lever**:

| FY25 → FY26 attribution | margin pts |
|---|---|
| ADR ex-FX | **+2.29** |
| FX | **+1.32** |
| Ops & support per night ($2.32 → $2.20) | +0.51 |
| G&A | +0.64 |
| Cost of revenue (GBV-driven) | −0.95 |
| Product development | −0.10 |
| **Brand & performance marketing ($2.99 → $3.40)** | **−1.78** |
| Field operations & policy | −0.46 |
| D&A and add-backs | −0.42 |
| **Total** | **+1.05** |

**If ADR ex-FX and FX both go to zero, the base case is a 2.5-point margin *decline*, not a 1-point gain.**

- **85% of the four-year rise in cash cost per night is sales and marketing** ($2.08 of $2.44: $1.18
  brand and performance, $0.90 field ops). Ops & support *fell* $0.14 and G&A fell $0.29.
- **AI customer support is real and worth ~+0.39 margin points a year, not 2.** Ops cash cost per night
  $2.130 → $2.049 (−3.8%) in 1H26. Management's own disclosures: AI resolves ~45% of contacts, support
  cost per booking −10% (1Q26) and −16% (2Q26). Verified end to end by the red team.
- **The realistic Adjusted EBITDA ceiling is ~38%** — BKNG's five-year EBITDA-proxy range is 30.0-37.4%.
  **P(FY2028 margin ≥ 40%) = 21%** on a 40,000-draw correlated Monte Carlo, and it happens through
  monetisation (+19.9bps of take rate a year) not through cost (support cost per night would have to fall
  16.4% a year for three years, against a best-ever realised −3.8%).
- **Below EBITDA it gets worse, and nobody models it.** FCF/EBITDA falls 107% (2025) → 99 / 95 / 93% as
  cash taxes converge on the provision and interest income falls. **SBC-adjusted FCF margin is 22.5-22.7%
  against a 35-37% headline. That 14-point wedge is the number the pitch has to defend.**

### 4.4 What changed vs the 5 Sep model, and why

| | 5 Sep | Tonight | Why |
|---|---|---|---|
| FY27 base revenue | $15,959M (+12.3%) | **$15,842M (+11.3%)** | WS10's regional build replaces a single +9% nights assumption; +2.5% ADR ex-FX replaces +3%; WS05's FX schedule puts −0.6pp on FY27 where the old model had zero. Partly offset by +$197M of new business |
| FY27 base margin | 36.5% | **35.9%** | Same lever stack, less 0.38pp of AI referral cost |
| FY27 base FCF | $5,825M | **$5,420M** | The old model set FCF = 100% of EBITDA; this one runs the bridge (95%) |
| FY27 net cash | $12,358M | **$10,116M** | **Correction.** RSU tax withholding (~$0.7bn/yr) was never subtracted. Worth ~$4/share on every EV lens |
| **FY27 base price (EV/EBITDA)** | **$248** | **$181** | **−$55 multiple, −$5 EBITDA, −$4 net cash, −$3 share count (WS18). The multiple is 82% of the change.** At 22x this model still gives $235 |
| FY27 bear | +4.3% / 33.8% | **+1.8% / 28.4%** | Four separate tails now stack: regional demand bear, strong-dollar path (−2.6pp), −15bp take rate, high AI referral cost |
| FY28 base growth | +11.0% | **+13.3%** | **An FX artefact, not a demand call.** FY27 carries a −0.6pp revenue FX drag and a −0.8pp timing wedge, both of which lap |

### 4.5 Price per lens

| Lens (FY2027E unless stated) | Multiple bear/base/bull | Bear | **Base** | Bull |
|---|---|---|---|---|
| EV / adj. EBITDA | 13.5 / 16.5 / 18.5x | $108 | **$181** | $234 |
| EV / FCF | 11.3 / 14.3 / 17.3x | $84 | **$153** | $218 |
| P / SBC-adjusted FCF | 15 / 19.5 / 24x | $37 | **$117** | $197 |
| P / earnings proxy | 15 / 19.5 / 24x | $45 | **$111** | $176 |
| EV / adj. EBITDA on FY2028E | same | $104 | **$218** | $289 |
| DCF, 10-yr fade to 3%, CoE 10.5% | — | $78 | **$183** | $281 |
| **Football field (low / mean / high)** | | **$37 / $76 / $108** | **$111 / $160 / $218** | **$176 / $233 / $289** |
| Upside vs $181.94, mean | | −58% | **−12%** | +28% |
| *Memo at 18 / 22 / 25.5x* | | *$140* | *$235* | *$315* |

**25/50/25 weighted:** $176 on the EV/EBITDA lens (−3.2%), **$157 on the football-field means (−14%)**,
$231 at the old multiples (+27%). WS12's own grid, run on the 5 Sep scenario EBITDA, gives **$190.5 vs
$249.0** — same conclusion, slightly different inputs.

**Reverse DCF, unchanged and that is the point.** At 10% CoE / 3% terminal, $181.94 discounts **7.50%**
a year FCF growth for ten years on reported FCF and **13.32%** on SBC-adjusted FCF — identical to the
5 Sep note's 7.497% / 13.322%. The base case compounds FCF at 9.9% FY26-FY28. **Priced at the base case
on reported cash flow; above the bull case after SBC.**

### 4.6 Against the Street

| | Street | Our base | Delta |
|---|---|---|---|
| 3Q26 revenue | $4,740M (Zacks, 7 est.) | $4,801M | +1.3% |
| **4Q26 revenue** | **$3,200M (10 est., 3,050-3,700)** | **$3,145M** | **−1.7%** |
| FY26 revenue | $14,100M / $14,160M | $14,233M | +0.9% / +0.5% |
| FY26 adj. EPS | $5.23 / $5.28 | $5.20 | −0.5% / −1.4% |
| FY26 FCF | $5,350M | $5,129M | −4.1% |
| FY27 revenue | $15,730M / $15,760M | $15,842M | +0.7% / +0.5% |
| **FY27 adj. EPS** | **$6.02 / $6.14** | **$5.67** | **−5.8% / −7.7%** |

**We are above the Street on revenue and below on FY27 EPS, and that is the honest version of the pitch:
more revenue, more SBC, more AI cost, fewer shares retired than the sell side assumes.** The 4Q26 gap is
**entirely FX** — the Street's $3,200M implies +15.2% y/y; ours implies +13.2% with the revenue FX line
contributing −0.4pp against +3.0pp in Q3.

### 4.7 What the model still cannot do

No reaction function (deliberate). FY2028 has no regional build and no FX view — which is why its revenue
growth is mechanically flattered. New businesses are a revenue line, not a segment, with a 70% incremental
margin that is an assumption with no disclosure behind it. No balance sheet below net cash and no float
model. **The bear's 1Q27 margin (13.3%) is arithmetically fine and economically odd** — seasonal spreads
are additive and there is no cost-response function; management would cut marketing. Buybacks are
exogenous and exceed the remaining $3.4bn authorisation. No Monte Carlo (three discrete scenarios plus a
7×7×9 grid in `13_scenario_grid.csv`).

---

## 5. Macro for the next 12-18 months, and how it reaches the print

**Bottom line: the macro risk to this stock is not to the KPI. It is (i) FX arithmetic in the reported
line, (ii) the multiple, and (iii) management's choice of words about the next quarter.**

Airbnb's nights have absorbed, in four years, a 500bp hiking cycle, a 27-point sentiment collapse, a
tariff shock, a 25% loss of Canadian inbound and a **+25.5% y/y airfare spike** — without once leaving a
7-12% growth band outside 2021-22 base effects. Spring 2025: Michigan fell 16.5 points y/y, Canadian
trips to the US fell ~25%, BEA inbound fell 5.0% — **global nights growth went from 7.9% to 7.4%. Half a
point.** 1H26: the largest airfare shock since 2022 coincided with **the fastest nights growth since
4Q24** (+10.3%; 4Q24 was +12.3% — WS15 correction #9).

And the gap that proves it: **Booking guided Q3 room nights to +3-5% and grew alternative-accommodation
nights +4%; Airbnb guided low double digits.** A six-to-seven point gap on the same underlying travel
demand. Whatever drives Airbnb's nights in 2026 is share, product and expansion markets — not the cycle.

### 5.1 The state of play (dated)

- **Fed at 3.50-3.75%.** 28-29 Jul 2026 hold was 9-3 with **all three dissenters preferring a HIKE**.
  June dots: 3.8% end-2026, 3.6% end-2027 — the median dot implies a hike. Market-implied hike probability
  ~60% on 4 Sep after a +162k payroll. New chair (Warsh) whose reaction function strategists say they
  cannot read. **This is the regime change most likely to be missed:** models built in 2025 assumed easing.
- **Dollar.** EUR/USD 1.161 on 4 Sep; **3Q26 QTD average 1.15 vs 1.17 in 3Q25 = −1.6% y/y, the first
  negative since 4Q24.** Reuters poll (2 Sep, 55-66 strategists): 1.16 / 1.17 / 1.18 at 3 / 6 / 12 months.
  The bank distribution splits into two camps — JPM/HSBC 1.10, GS 1.12, Citi 1.13-1.14 against Nomura 1.22-1.25,
  Scotiabank 1.20-1.21, UBS 1.18-1.20. **The 15-point gap between the camps is worth ~5.5pp of ADR FX,
  bigger than any plausible demand scenario.**
- **Energy.** EIA STEO (11 Aug) has Brent $86.81 (2026) → **$69.39 (2027)** and jet fuel $3.24 → $2.50/gal.
  **The STEO is already stale**: Brent was $96.06 on 4 Sep after renewed attacks. Capital Economics has
  $100 by end-2026 falling toward $70 in 2027 — same landing point, higher path.
- **Hotels.** CoStar/Tourism Economics: FY26 US RevPAR +4.4% / ADR +3.1%; **FY27 RevPAR +2.1% / ADR +1.6%,
  explicitly below inflation**, with June 2027 RevPAR at −0.8% on the World Cup comparison.
- **Consumer, two-sided.** Surveys recession-adjacent (Michigan 55.2, Conference Board expectations 68.2);
  hard data fine (unemployment 4.1%, claims 206k and −10.4% y/y, card delinquencies improving). **The
  surveys have never mattered for Airbnb's nights (r −0.05).**

### 5.2 Transmission, quantified

| Channel | Coefficient | FY27 effect |
|---|---|---|
| Broad USD → ADR FX | **−0.715 pp per pt** (n 17, r −0.964) | consensus path −0.1pp; strong-dollar −2.8pp; weak +1.9pp |
| EUR/USD (lagged 1-2q) → revenue FX | **+0.413 pp per pt**, intercept −0.640 (n 17, r +0.80) | **consensus −0.6pp; strong-dollar −2.6pp; weak +0.9pp** |
| Broad USD → EBITDA margin (chained) | **−0.28 pp per +1% USD** | via the two FX channels, before any cost response |
| Airline-fare CPI → ADR ex-FX | +0.067 pp per 1% | **fares from +21% to ~−5% costs −1.3 to −1.7pp of FY27 ADR ex-FX.** Not in the driver model |
| Everything else → nights | **zero** | 1,408 pairs, 0 high-confidence |

**The FX schedule (base case, pp):**

| | 3Q26 | 4Q26 | 1Q27 | 2Q27 | 3Q27 | 4Q27 | FY27 |
|---|---|---|---|---|---|---|---|
| Revenue FX | **+3.00** | **−0.43** | −1.03 | −0.80 | −0.61 | −0.07 | **−0.63** |
| ADR FX | +0.80 | −0.36 | −0.40 | +0.02 | +0.66 | +0.49 | +0.19 |
| Timing wedge | +2.18 | −0.07 | −0.63 | −0.82 | −1.26 | −0.56 | −0.82 |
| Driver already realised | 100% | **84%** | 34% | 0% | 0% | 0% | |

**Read the 4Q26 column first. It is the same −0.4pp under all three dollar paths, because 84% of its
driver is FX that has already happened. That is the sharpest thing anyone can say on 5 November.**

And the consequence for 2027 that will be misread: **3Q27 revenue growth (+9.9%) is the low point of the
path and it is entirely the FX lap** — 3Q26 carries +3.0pp and 3Q27 carries −0.6pp, while nights growth in
that quarter is +8.9%, in line with every other. 4Q27 (+12.7%) re-accelerates for the same reason in
reverse. *Anyone reading this model as a demand call in 2027 is reading the dollar.*

### 5.3 Scenarios (WS05, 30 / 50 / 20)

| | A. Energy relief, soft dollar (30%) | B. Muddle through (50%) | C. Recession or renewed shock (20%) |
|---|---|---|---|
| EUR/USD | 1.21-1.25 | 1.16-1.18 | 1.09-1.13 |
| FY27 nights | +10.5% | **+8.5%** | +5.5% |
| FY27 revenue FX | +0.9pp | **−0.6pp** | −2.6pp |
| FY27 revenue | +14.8% | **+10.5%** | +3.0% |
| FY27 margin after cost response | 37.3% | **36.5%** | 34.7% |

Probability-weighted: **FY27 nights +8.5%, revenue +10.3%, margin 36.4%.** Note WS15's ruling (CONF-01,
CONF-02): this is *not* an independent estimate to average with WS10's +12.4% or WS13's +11.3% — it
shares the same FX schedule and imports its margin anchor. Carry **+10.3% as the macro-adverse case**,
not as a fourth opinion.

### 5.4 "What would change our mind" — dated

**Before 5 November**

| Date | Release | Threshold |
|---|---|---|
| Daily to 30 Sep | EUR/USD, broad dollar | **September average below 1.14 → 3Q26 ADR FX goes below −2pp and reported ADR drops to ~+2%** |
| 11 Sep | Aug CPI | Airline fares below +15% y/y pulls the ADR ex-FX nowcast toward +3% |
| **15-16 Sep** | **FOMC + SEP** | **A hike plus a higher 2027 dot pushes the dollar to the strong path and takes 1-2pp off FY27 revenue growth** |
| 30 Sep | Personal Income & Outlays (Aug) | BEA accommodations below +2% y/y = the first coincident sign of US softness in the series that actually co-moves |
| 2 Oct | September jobs | Unemployment ≥4.4% or claims turning positive y/y flips the ADR ex-FX watch-list negative |
| **20-31 Oct** | **BKNG (~28-29 Oct), MAR, HLT, EXPE, airlines** | **A BKNG Q4 room-night guide below +3%, or a second hotel FY26 RevPAR cut, is the strongest available evidence of a genuine industry turn.** BKNG's alt-accom growth vs its own total is the ABNB share read |
| 27-28 Oct | FOMC (no SEP) | Second hike or a pause signal |
| 3 Nov | US midterms | Tape volatility two days before the print |
| **5 Nov** | **ABNB Q3** | **The one number: Q4 nights guided at or above the Q3 rate.** If it is, the ~3pp FX-driven revenue step-down is noise |

**Before the pitch (December)**: 6 Nov jobs; 10 Nov CPI (the airfare lap starts to show); **8-9 Dec FOMC
with SEP — the 2027 dots that set the dollar path under our FY27 revenue FX**; 10 Dec CPI;
**11 Dec government funding expires** (a shutdown suppresses the CPI/PCE releases the nowcast depends on,
as in Oct-Nov 2025); the November and December EIA STEOs (does the 2027 Brent path stay near $69 or get
revised toward the $96 spot?); and EUR/USD daily, because 1Q27's revenue FX is 34% locked at quarter end.

**What would falsify this note:** (1) a 3Q26 reported revenue FX materially away from +3pp (below +1.5 or
above +4.5) breaks the lagged spec; (2) a quarter where nights move >2 points on a macro variable with no
product or comp explanation resurrects the macro-to-nights channel we have declared dead; (3) a Q4 guide
where management attributes the step-down to *demand* rather than FX.

---

## 6. Alpha: what is tradeable and what is a talking point

**Bottom line: almost nothing here is tradeable, and saying so is the single most defensible position
the team can take in a Q&A.**

### 6.1 What survives

| Finding | Statistics | Tradeable? |
|---|---|---|
| **FX → ADR** | WF 0.44x naive, r 0.96, 8/10 signs, real-time | **Yes, as a forecast input.** No, as a trade — it does not move the stock. It is the one number the pitch should quote and the one card item most likely to be right |
| **Nights vs Street nights → 20-day drift** | n 18, LOO **+0.13** (n 11 post-2022, LOO +0.18), jackknife-stable r 0.35-0.57 | **Not yet.** 18 observations, a StreetAccount consensus quoted only when CNBC chose to quote it (an unruled-out selection channel), and it comes from a file with 97 tests. Two clean out-of-sample confirmations (5 Nov, Feb) would make it pitchable |
| **"Short the pop"** (R2) | 20d +5.89% (t 2.34, p 0.042), 60d +12.82% (t 2.30), LOYO-stable | **No.** Five of seven winners are pre-2024 and it **lost in both 2026 prints** (−6.1% Q4'25, −2.8% Q2'26). A de-rating-era rule |
| **May short** (R7) | 6/6, +14.4%, t 6.19, p 0.002, LOYO +13.4 to +16.6% | **No** — constructed after reading the seasonality table, and it is the same fact as the seasonal block, not independent evidence. n = 6 among 54 tests |
| **Guide below Street** | **9/9** negative at 20d, base-rate p **0.057** | A risk flag for sizing, not a trade |
| Prior-quarter S&M deleverage → next day-1 | r +0.59, n 17, LOO R² 0.24 | **Pre-registered hypothesis only.** One hit in ~60 tests, sign not pre-specified. Score it on 5 Nov |
| Jobs-day abnormal return | +1.04% per payroll release, t 2.47, n 60 | Economically sensible for a discretionary-travel name; **log it, pre-register the next 12 releases, do not trade it** |

### 6.2 What does not survive

Run-up into the print (r −0.004 with day 1). Buying after a down print (drops do not bounce, at any
horizon). Every momentum variant (consistent with a **−0.53 FF momentum loading**, t −7.7 — ABNB is an
anti-momentum name). Peer read-across (2 nominal hits in 24 tests with contradictory signs). Analyst
actions outside a print week (PT raises **−0.2%, p 0.25**). Short interest (2.17%, three-year low,
|r| ≤ 0.15 with forward returns). The price-target premium (r +0.44 looks powerful and **is quarterly
mean reversion in disguise** — trailing 3-month excess predicts the next quarter at r −0.71; both halve
and lose significance from 2023). Buyback announcements (never off-cycle; always inside the letter).
Product launches (both Summer Releases inside noise). **Every dated European regulatory event** —
Barcelona 2028, Spain's removal order, the €64.1m fine, the registry annulment, the EU data regulation —
all inside a 2σ band, which is a direct, dated counterweight to the regulatory bear case.

### 6.3 Options

**The 5 Nov event is not yet in the term structure.** On 5 Sep the Nov-20 straddle (13.38% of spot, 76dte)
and the Dec-18 straddle (15.65%, 104dte) scale as √time to within **0.002 points** — an implied event
premium of **zero**. The historical base rate is mean absolute day-1 move **7.07%**, median 6.87%, with
10 of 23 prints ≥8% and 5 of 23 ≤1.1% (the distribution is bimodal: big or nothing).

**This is the cheapest concrete trade-structure input the team has.** Re-run `09_stock_behaviour.py` in
the last week of October once the 6 Nov weekly is listed: **below ~7% implied the straddle is cheap
against the base rate; above ~9% it is rich.**

### 6.4 The honest statement

*Tradeable:* the FX-to-ADR forecast as a model input; a straddle decision in late October if the implied
move diverges from the 7.1% base rate; a "guide below Street" risk flag on position sizing (9/9, mean −8.90%; WS16 re-run on `16_reaction_tests.csv`).

*Pitch talking points, not trades:* the nights-drift coefficient (needs confirmation), the
nights-acceleration base rate, the May and November seasonals, the post-print fade, the S&M-deleverage
tilt.

*Neither:* everything in the alt-data layer, all management language features, all positioning measures,
all peer read-across.

---

## 7. Pre-registered prediction card for 5 November 2026

Guide (2Q26 letter, 6 Aug 2026): revenue **$4,690-4,770m, +15-17%**, inclusive of an approximate **3
percentage point FX tailwind after hedging**; GBV growth mid-teens on **low-double-digit** nights; ADR up
moderately; adj. EBITDA margin **down slightly** vs 3Q25's 50.1%; FY26 revenue growth **at least mid
teens**; FY26 margin **at least 35.5%**; implied take rate relatively flat vs 2025's 13.41%; no
significant Middle East impact assumed. Base comparisons: 3Q25 revenue $4,095m, nights 133.6m, ADR
$171.29, take rate 17.88%, margin 50.1%; 4Q25 revenue $2,778m.

| # | Metric | **Our estimate** | Range | Street | Guide | Mechanism | What we conclude if wrong |
|---|---|---|---|---|---|---|---|
| 1 | **Nights & seats y/y** | **+10.2%** (147.2m) | 7.9% to 12.6% (bear 144.2m, bull 150.4m) | no published consensus; WS04 derived bar **144-146m** | "low double digit" (10-12%) | WS10 regional build (NA +7, EMEA +8, LatAm +18, APAC +17), less the RNPL/three-feature lap in NA | **Below +9%:** the 1H26 acceleration was the three-feature lap (RNPL + cancellation redesign + single fee) and FY27 nights come down 1-2pts. **Above +12%:** expansion markets are compounding faster than the regional build assumes; raise FY27 nights |
| 2 | **ADR y/y** | **+3.8%** ($177.84) | +2.8% to +4.8% | **none published yet, but one will be**: Zacks quotes a 'GBV per Night and Experience Booked (ADR)' consensus 2-3 days before each print (2Q26 $181.56; 1Q26 $178.54; 4Q25 $165.52; 3Q25 $166.67; 1Q25 $170.55). ABNB has beaten it 5 of 5 by +0.5% to +4.6%. Get the Q3 number on ~2-3 Nov | "up moderately" | ex-FX run-rate ~+3.0-3.25% plus FX | **Above +5%:** the ex-FX pricing story changed — check bedroom mix before crediting price. **Below +2%:** either the dollar moved more than the fit says or mix reversed |
| 2a | **…of which FX** | **−1.3 to +0.8pp, centred near zero** | same | — | ~3pp of *revenue* FX (a different line) | Broad-USD fit gives +0.80pp (r −0.96); **EUR/USD fit gives −1.27pp for the same quarter and has the higher in-sample r** (CONF-05). WS10's revenue-weighted spot basket is +0.32% | Outside the range → refit. This is the most mechanical item on the card and the one we most expect to be right |
| 3 | **GBV** | **$26,185m** (~+14.3%) | $25,391-27,013m | — | "mid teens" | nights × ADR | A GBV/nights/ADR triangle that does not close means one of the three is mis-measured |
| 4 | **Revenue** | **$4,801m (+17.2%)** | **$4,78-4,82bn is the honest card range** (WS15 CONF-04); full scenario span $4,632-4,977m | **$4,740m** (Zacks, 7 est., 4.72-4.77) | $4,690-4,770m | Four methods: WS10 bottom-up **$4,775m**; WS02 trailing-8 cushion **$4,815m**; WS04 post-2022 median beat **$4,832m**; WS08 raw backlog **~$4,590m** (~$4,720m with the RNPL add-back) | **Below $4,740m:** the first sub-Street revenue print in 23 quarters — a regime change, not a miss. **Above $4,850m:** the cushion did not shrink after all; revert to the full-history cushion |
| 5 | **Adj. EBITDA margin** | **49.0%** | 48.3% to 50.2% | derived bar $2,300-2,400m of EBITDA | "down slightly" from 50.1% | WS07 lever stack; 9 of 10 such ceilings met, by a mean of 1.4pts | **Below 48%:** the FY 35.5% floor is at risk for the first time in four years. **Above 50%:** the FY guide goes to 36%+ and the marketing ramp is easing |
| 6 | **Brand & performance marketing y/y** | **~+17-25%** (base needs H2 at ~+17%) | 1H26 ran **+32%** | not disclosed by the Street | none | **The single most informative line in the release.** FY26 margin = 37.0% at +17%, 36.2% at +25%, **35.5% at +31%** | **Above +28%:** the FY lands at the 35.5% floor, not 36%+. **Below +20%:** the first evidence the reinvestment cycle is easing — worth more to the margin case than any AI datapoint |
| 7 | **Implied take rate** | assumed **17.88%** flat; **reported ~18.27%** | 17.83-17.93% assumed | — | "relatively in line y/y" | +2.2pp of FX timing sits between the two. **A reported 18.3% is consistent with completely flat monetisation** | **Do not call the single fee a success on a reported take rate near 18.3%.** A reported rate *below* 17.9% with a positive FX wedge would be genuine compression |
| 8 | **4Q26 revenue guide** | **midpoint implying +11-13%** (our model $3,145m, +13.2%) | +8.5% to +17.5% | **$3,200m = +15.2%** (10 est., 3,050-3,700 — a 21% spread, by far the widest on the table) | none yet | **~3.4pp of the step-down from the Q3 15-17% is the FX lap, and 84% of it has already happened** | **A guide at +11-13% is arithmetic, not deceleration** — but the Street's $3,200m falls, and that is a live "guide below Street" setup (**9/9** negative 20-day, base-rate p **0.057**). Below +9%, or nights guided down, is the bear case |
| 9 | **FY26 guide changes** | revenue raised from "at least mid teens" to **high teens or a point ~16-17%**; margin floor replaced by "**approximately 36%+**" | — | FY26 $14,100-14,160m | "at least mid teens" / "at least 35.5%" | The FY guide has **only ever been raised**, and in 2024 and 2025 the raise landed at the Q3 print. 1H26 is already +17.1% | **A mere reiteration would be the first non-raise since the FY revenue guide existed** — a red flag out of proportion to its arithmetic |
| 10 | **Likely language** | full-year framework **with a number** in prepared remarks; "expansion markets", "bedroom nights", AI support metrics; single-fee completion reaffirmed; **no FY27 guide** | — | — | — | Long-term-target share of prepared remarks: the 11 calls with any averaged **+4.0%** day-1, the 12 with none averaged **−2.7%** (sign hit rate 6/11 vs 5/12 — the *mean* separates, driven by tails) | **If the prepared section drifts into expansion-market and Experiences narrative without a full-year figure, that is the 2Q24 / 1Q23 pattern.** Any hedged 2H/2027 macro sentence — "moderation", "shorter lead times", "pressure on growth rates later in the year" — cost 8-13% in 2022, 2023, 2024 and 2025, **and did not verify in either 2024 or 2025** |

**On ~2-3 Nov, pull Zacks' "Wall Street's Insights Into Key Metrics Ahead of Airbnb (ABNB) Q3
Earnings."** It publishes the nights, ADR and GBV consensus free, two to three days before the print
(2Q26: nights 145.44m, ADR $181.56, GBV $26.42bn). That closes the card's single biggest hole — the
unpublished nights bar — at zero cost. Read it against WS04's derived 144-146m and expect a 1-2% vendor
gap versus StreetAccount (Zacks had 2Q25 nights at 130.76m where WS04's StreetAccount row has 133.35m).
ADR belongs on the card too: ABNB has beaten the published ADR consensus 5 of 5, and on n=5 the
correlation with the day-1 move is **−0.46** — treat a large ADR beat as a mix/FX signal, not a bull
signal. *(WS16)*

### 7.1 Expected reaction under each outcome

Base rate for the day: mean absolute day-1 move **7.07%**, median 6.87%; day-1 excess positive 11 of 23;
10 of 23 prints moved ≥8%. **The print is a coin flip in direction and a big number in size.** One turn of
EV/NTM EBITDA = **$9.11 = 5.0%**; a typical print moves the forward multiple ~1.5 turns.

| Outcome | Analogue | Expected day-1 | Then |
|---|---|---|---|
| **Nights ≥ +11% and Q4 nights guided at or above the Q3 rate** | 4Q22 (+13.4%), 4Q24 (+14.4%), 2Q26 (+17.4%) | **+5% to +10%** (post-2022 accelerating prints average +6.7%, n 5) | Historically the move *extends*: post-2022 20-session excess +1.3% for accelerating. But **up-prints have drifted −7.1% at 20d / −14.8% at 60d across the full sample**, and November has been negative 5 of 5. Frame it as "the burden of proof is on why this sustains", not as a short |
| **Nights +10% and Q4 revenue guided +11-13% with FX quantified** | 4Q25 (+4.6%), 3Q25 (+0.3%) | **−2% to +5%** | The likeliest single outcome. The Street's $3,200m comes down; whether that is read as FX or as demand is decided by whether management quantifies the Q4 FX assumption **in the letter** |
| **Q4 revenue guided +11-13% but the FX assumption is *not* quantified** | 1Q23 (−10.9%) | **−5% to −10%** | The specific risk of this print. A mechanical 3.4pp FX lap read as a demand deceleration. **Have the bridge ready before the guide, not after** |
| **Nights guided below the Q3 rate, or "moderation"/"lead times" language** | 3Q22 (−13.4%), 2Q24 (−13.4%), 3Q24 (−8.7%), 2Q25 (−8.0%) | **−8% to −13%** (post-2022 decelerating average −5.4%, n 9) | Post-2022 20-session excess for decelerating prints is **−8.0%** — the move extends. But note that the 2Q24 and 2Q25 cautions **both proved wrong within two quarters**; that is where the 5-20 session reversal trade lives, not the day-1 trade |
| **Nights ≥ +12% and FY26 revenue raised to a point ≥16%** | 2Q26 | **+10% to +17%** | This is the only outcome that justifies re-rating toward 20x. On the +0.48-turns-per-point slope, a Q4 guide implying **>18%** revenue growth is worth ~2 turns ≈ $20/share and would be the first evidence since 2021 that the growth regime genuinely changed |

**Positioning going in gives no cushion.** Spot $181.94 is **above** the mean target ($178.96 across 46);
55% of targets sit below spot; 46% of ratings are Hold or worse; **22 raises and 0 cuts since the 2Q26
print and the stock still outran them**; short interest 2.17% (three-year low, no squeeze fuel); ABNB
enters at 18.2x forward EBITDA, its post-2022 median, with the guide implying 17.8% growth against 15.7%
consensus. **The asymmetry has flipped versus the last two prints.**

### 7.2 Score these regardless of the outcome

Nine pre-registered items to score on 6 November — this is how the team learns which of tonight's work was
real: the FX-to-ADR fit (**+0.8pp broad-USD vs −1.3pp EUR**, which one was right); the funds-held backlog
nowcast (**+12.0% vs a guided +14.5-16.5%** — if the funds-held-minus-GBV gap widens again from 5.2pp, the
indicator is broken like unearned fees and should be retired); WS08's implausible nights nowcast (+22.9%);
the margin nowcast (49.1-49.8%); the nights-acceleration sign rule (17/21 so far); the pre-registered
S&M-deleverage tilt; the revenue-vs-cushion methods (four of them, spanning $4.59-4.83bn); WS10's
regional calls; and the guide-below-Street flag on the Q4 number.

---

## 8. Pitch implications

### 8.1 The variant perception

**The market is arguing about the wrong quarter.** The consensus debate on ABNB is whether the 2026 nights
re-acceleration is real. That debate is *settled in Airbnb's favour and already priced* — the stock
re-rated from 13.3x forward EBITDA (Nov 2025) to 18.2x, and 84% of the +17.4% on 2Q26 was multiple, not
estimate. The two things that are **not** priced, and that our work can quantify from primary sources:

1. **FY27 reported revenue growth is going to look worse than FY27 demand, and the reason is entirely a
   dollar lap that is already knowable.** Revenue FX goes +3.0pp (3Q26) → −0.4pp (4Q26) → −0.6pp (FY27),
   and 84% of the 4Q26 driver has already happened. 3Q27 will print the slowest revenue growth of the
   path (+9.9%) on *unchanged* nights growth (+8.9%). **A team that walks into the Q4 guide with the FX
   bridge already built has a two-quarter information advantage over a Street that will read a mechanical
   lap as a demand break.**
2. **Half of ADR growth is a bigger unit, not a higher price** — bedroom nights +12% vs nights +10%,
   ≤$102.87 per bedroom-night vs $171.74 for a US hotel room. That makes ABNB's ADR *more* defensible than
   the "affordability crisis" bears think **and more cyclical than the bulls think**, because size mix is
   discretionary and reverses in a downturn.

**And the uncomfortable third leg the pitch must own:** on the evidence we now have, the base case is
worth about **$181** against a **$181.94** spot. *If the recommendation is a long, the upside has to come
from FY27 revenue above ~$16.0bn, SBC below ~10% of revenue, or a separately priced optionality bucket —
not from the exit multiple.*

### 8.2 The three strongest evidence-backed claims

1. **"The FY27 revenue optics are a dollar lap, and we can date it."**
   `revenue FX = −0.640 + 0.413 × mean(EUR/USD y/y at t−1, t−2)`, n 17, r +0.80, validated out of sample
   against management's own quantified +3.0pp for 3Q26 (fit: +2.2pp — close, and far closer than the
   contemporaneous fit's −1.6pp, but **not exact**, per WS15 correction #8). 4Q26 is **−0.4pp under all
   three dollar paths** because 84% of the driver is realised. *Independently corroborated by WS10: the
   revenue-weighted spot basket is only +0.32% y/y in 3Q26 QTD, so the guided "approximately 3 percentage
   point tailwind" is hedges plus the check-in lag, and neither survives into FY27.*
2. **"Airbnb is taking share again, for the first time since 2022, and we can measure it in nights."**
   Booking.com's alternative-accommodation room-night growth premium over its own total room nights has
   gone from **+6 pts (3Q24) to −1 pt (2Q26)**: alt-accom +4% against Airbnb's +10.3%. Verified against
   the SEC-filed BKNG Q2'26 release. Corroborated three ways: Airbnb's nights growth is ~5x AirDNA's US
   category demand growth (+2.0%); EU27 platform nights are growing ~8 points faster than total European
   nights while Airbnb grows with the platform category; and Airbnb guided Q3 nights to low double digits
   against Booking's +3-5% room-night guide. **Nights, not listings, is the only clean share metric** —
   European manager inventory is listed non-exclusively and double-counted across platforms.
3. **"The multiple is set by forward growth and by nothing else — including margin — and that is why the
   margin debate is the wrong debate."**
   +0.48 turns of EV/EBITDA per point of NTM revenue growth (t 8.3 levels, +0.49 t 5.6 in 12-month
   changes, consistent in sign and size across levels, changes, quarterly, monthly and the cross-section).
   Margin: t 0.3 in the time series, t 1.3-1.5 in the cross-section, and the apparently strong negative
   coefficient on EV/EBITDA is the mechanical −1/margin artefact. Reported alongside its own
   Durbin-Watson failure, which is why the 12-month-change specification is the one quoted.

### 8.3 The three weakest claims the team should stop making

1. **"18 / 22 / 25.5x exit multiples."** No method and no live sell-side target supports them. The highest
   target on the tape ($220) implies 19.3x; the mean implies 15.4x. Replace with **13.5 / 16.5 / 18.5x**
   and show the old grid as an explicitly labelled *"if the market keeps paying 2026 multiples"*
   sensitivity. (WS15 correction #20 — `model/assumptions.md` still carries the old set at the top; WS13's
   appended section carries the new one.)
2. **"Zero of 233 alt-data features beat AR(1)" and "funds held forecasts revenue at 0.6x naive."**
   Both are wrong as written and they contradict each other. The finished file has **598 rows, 52 of which
   beat AR(1)**; the funds-held pair is 0.59x AR(1) on one window and **1.85x on the other, from the same
   file**. The defensible version: *nothing in the alt-data layer beats AR(1) on both evaluation windows,
   and every apparent winner is either mechanical FX, not knowable before the print, or window-dependent.*
3. **The single-fee / take-rate bull case, in all its forms.** Specifically stop saying: *"Reserve Now Pay Later added
   3 points of nights growth"* (it was **three features together** — RNPL, the cancellation-policy
   redesign and the single-fee migration — and WS11 propagated the misattribution into a 3pt FY27 nights
   haircut); *"a −0.8pt take-rate hit from the direct-booking pilot"* — the pilot is now **verified** (Airbnb's
   own product copy on its host community forum, 28 Aug 2026; RSU by PriceLabs, 31 Aug 2026: host fee
   15.5% → **6% or 10%** on host-generated tracked links, invite-only, US, no newsroom post). The number
   is wrong for a different reason: −0.8pt of a ~13.4% take rate requires **8.4% of all GBV** at the 6%
   tier or **14.5%** at the 10% tier. **Use 0-15bp of FY27 take rate; reserve −0.8pt for a "pilot becomes
   policy" tail**; and
   *"discount share tripled from 11% to 31% between March and August 2026"* (mislabelled — those are
   cross-city medians, not quote-weighted shares, which went 17.3% → 31.4% — and confounded by a mid-series
   scrape change: the share of quotes carrying a taxes line went 0.20% → 5.65% → 6.54% over the same dumps
   and NYC swings 41.5 → 25.3 → 43.5).

   *The take-rate arithmetic that is defensible:* the single 15.5% host fee is worth **+40 to +50bps if the
   replaced blended guest fee was 14.1%, −15bps at 15.0% and −124bps at 16.5%**. Management's "modest
   upside" implies the low end. Three of five Third Bridge experts independently say the OTA take rate is
   at a ceiling; the European expert's phrase is that Airbnb and the rest have "set a plateau".

**Two more to retire:** *"the only out-of-sample signal in 97 tests"* (there are nine, and the correct,
still-strong statement is that **every positive-LOO spec is at 20 days and not one is at day 1**); and
*"nights per listing has been 62.5-62.7 for four years"* — say "flat within the rounding of the
disclosures", because the inputs are "over 8 million" and "over 9 million".

### 8.4 Risks, with probabilities

| Risk | Probability | Size | Evidence |
|---|---|---|---|
| **The multiple does not re-rate above ~16.5x** | **~65%** — this is the base case on the evidence | The whole thesis: $55/share | Three independent methods; no live target implies >19.3x; margin does not move it and forward growth is decelerating from FY27 on the FX lap |
| Q4 revenue guide read as demand rather than FX | **~35%** | 5-10% on the day; recoverable | **9/9** guide-below-Street prints had negative 20-day excess; the offsetting evidence is 4Q24, when the guide came in below Street and the stock rose 14.4% on the nights beat |
| **FY27 nights disappoint on the three-feature lap** | **~30%** | 1-3pts of nights = ~$0.3-0.5bn of FY27 revenue | +3pts of Q1'26 nights and +4pts of GBV came from RNPL + cancellation redesign + single fee together; RNPL laps in the US from 3Q26. WS10 already has NA at high-single |
| Strong-dollar path (JPM/HSBC/GS camp: EUR/USD 1.09-1.13) | **~25%** (WS05 scenario C weight is 20%, and the bank split is roughly 40/60) | **−2.6pp on FY27 revenue, ~−1.5pts of margin through the chain** | 25 bank forecasts split into two camps 15 points apart, worth 5.5pp of ADR FX |
| SBC stays at ~13% of revenue through FY28 | **~70%** | The 14-point wedge between a 36% EBITDA margin and a 22.5% SBC-adjusted FCF margin; **on EV/NTM SBC-adjusted FCF ABNB is exactly at the peer median** | Model has SBC at 12.6 / 12.4 / 11.8%; management guides "flat to slightly down". Mitigant: buybacks fund it — diluted shares 649M (2Q24) → 597M (2Q26), −8% in two years, net cash return after SBC positive every quarter since 3Q22 |
| Regulation costs >1% of revenue | **19.5% by 2027, 70.7% by 2030** | median 0.87% of revenue by 2028; **p95 3.96%** | 93% European; 68% of the 2027 variance is two EU items. **Mitigant: no European regulatory event has ever moved this stock**, and the 9 Sep EU proposal's modelled expected value is 0.18% of 2027 revenue |
| AI disintermediation | **not a 2026-27 issue**; the 2028 mid case is ~5% of GBV via paid referral | FY28 **$329m = 1.9% of revenue = 5.3% of EBITDA** (high case 3.83% / 10.6%) | Booking disclosed AI tools at **<1% of room nights** in 2Q26; the Third Bridge AI expert sees ~3% of bookings moving AI-native in 12-24 months with **no EBITDA impact**. **The honest framing is not "AI kills Airbnb" — it is "AI turns 5-10% of Airbnb's free traffic into paid traffic by 2028." That is a multiple story, not an earnings story** |
| FY28 margin ≥40% (the bull's requirement) | **21%** | — | 40,000-draw correlated Monte Carlo; p10/median/p90 = 33.3 / 37.6 / 41.3. It happens through monetisation (+19.9bps of take rate a year), not cost |
| The share cap: base case needs **51.5% of global STR gross bookings by 2028** | — | The arithmetic a good push-back will use | Airbnb is 41.5% of Phocuswright's $219.9bn 2025 pool; the base needs ~2.5pts a year for four years on a 5.3%-CAGR market. It added ~3.2pts a year 2019-24, so not unprecedented — but that was the platform-consolidation window. **The bull's 57.6% by 2029 I would not underwrite** |
| November calendar | 5 of 5 negative, −5.1% vs QQQ | — | Whatever the direction, November is a headwind for a long entered on the print |

---

## 9. Build-forward list, ranked

Ranked by what it unlocks before the December pitch, per unit of effort.

| # | Item | Hours | Owner | Unlocks |
|---|---|---|---|---|
| 1 | **Refresh the FX schedule weekly to 5 Nov and rebuild `05_fx_schedule.csv` daily through 30 Sep.** Add the Airbnb-weighted 22-currency basket (WS01 D269) instead of the broad dollar | **1 + 10 min/week** | Krish | The one index the pitch should quote; locks the 4Q26 and 1Q27 revenue-FX numbers before anyone else has them. **Highest value per hour in the run** |
| 2 | **Re-run the options block in the last week of October**, once the 6 Nov weekly is listed | **1** | anyone | Converts "no event premium at 76dte" into an actual implied-vs-7.1%-base-rate comparison and gives the card a trade structure |
| 3 | **Freeze and publish the prediction card (section 7) before 5 Nov, then score all nine items on 6 Nov** | **3 + 3** | Krish | The only way to learn which of tonight's work was real. Also the single most credible slide in a Q&A |
| 4 | **Reconcile the four FY27 revenue estimates into one number with the others as an explicit range**, and update `model/assumptions.md`'s exit multiples to 13.5/16.5/18.5x with the old grid as a labelled sensitivity | **2** | Krish | Removes the deck's biggest internal inconsistency (CONF-01, CONF-13). **Do this before any slide is drawn** |
| 5 | **Get a nights whisper for Q3-26.** A free one publishes ~2-3 Nov: Zacks' *"Wall Street's Insights Into Key Metrics Ahead of Airbnb (ABNB) Q3 Earnings"* carries nights, ADR and GBV consensus (2Q26: nights 145.44m, ADR $181.56, GBV $26.42bn). Buy-side colour is still worth having earlier, but the bar is no longer unobtainable | **0 calls, 10 min on ~2 Nov** | whoever has buy-side contacts | The only variable in the whole study with out-of-sample power (LOO +0.13 at 20 days) currently has no bar to beat |
| 6 | **Merge WS04's 23 rows into Theo's `consensus_snapshots.csv`** and rebuild `12_abnb_multiples_monthly.csv` on consensus instead of the guide proxy | **3** | Krish / Theo | Removes WS12's caveat C2 (the panel's forward multiple is ~1.5 turns low), sharpens the print-day decomposition, and stops the guidance dataset reporting "missing" |
| 7 | **Monthly Inside Airbnb capture on the fixed 13 cities**, same calendar day, storing listings / `reviews_ltm` / `reviews_l30d` / blocked share at 30-90-180d / entire-home share / calendar median price | **2 + 30 min/month** | Krish | The fixed panel currently has **n = 0** usable quarters. Twelve captures give the first real y/y. **Inside Airbnb's CDN keeps ~1 year: a month missed is a month lost.** Also turns the quote-discount series into a true y/y by March 2027 |
| 8 | **Move Theo's D190 (Bloomberg exports: 6,365 rows of consensus estimates and revisions) off the external volume**, then D142 (67.5M Inside Airbnb reviews, 120 markets) and D170 (25 municipal STR registries, 109,343 rows) | **2 + Theo's time** | Theo | D190 closes the largest single gap in the 217-row census. D142 makes review velocity a global monthly demand proxy. D170 turns "enforcement" from an assumption into a measurement |
| 9 | **Price the optionality bucket separately** (hotels / Experiences / Services / ads), sized from WS11's scenarios, rather than adding turns to the core multiple | **4** | Krish | The only intellectually honest route from $181 to a higher number |
| 10 | **Standardise the "nights acceleration" definition** across WS01/04/05 and restate it as a base rate with its n | **1** | Krish | Three notes give three different counts (17/21, 9, 5) of the same fact. It is on the card; it cannot be ambiguous |
| 11 | **Renumber `research/sources/README.md`** — S30, S32, S33, S34, S35, S36 and S37 each appear twice with different meanings | **1** | anyone | Citations of the form "(S33)" are currently ambiguous. Do it before the deck cites sources |
| 12 | **LatAm external benchmarks** (Embratur, DATATUR, a Brazilian domestic travel indicator) and **US NTTO monthly arrivals** | **4-6** | Krish | LatAm is 15% of nights and contributed 2.96pp of 2Q26's 10.3pp with **zero external validation**. The strongest LatAm correlation in 3,446 tests is with *French* Eurostat platform nights |
| 13 | **Log the funds-held and unearned-fee balances the day each 10-Q posts**, with the RNPL language alongside | **0.5 + 15 min/quarter** | anyone | The only live backlog indicator is being distorted by a product change; tracking the funds-held-minus-GBV gap (3.8pp at 2Q25 → 5.2pp at 2Q26) is the only way to calibrate it |
| 14 | **Marriott and Hilton *regional* RevPAR** from the quarterly releases, backfilled 2023-26 | **3** | anyone | Turns the peer file from one global number into four regional ones and gives NA and EMEA a same-region hotel benchmark |
| 15 | **13F concentration history from EDGAR** (13F-HR tables, ABNB CUSIP 009066101, quarterly since 4Q20) | **4** | anyone | The one WS09 test that could not be run. **Do not cite a 13F trend we have not measured** |
| 16 | **Weekly Google Trends capture with the pull date stamped** | **0.5 + 5 min/week** | anyone | **Cheap insurance only.** Trends does not forecast the print; but because Google renormalises history on every pull, storing vintages is the only way a point-in-time claim could ever be made |

**Explicitly do not build:** a broader composite demand index (all three failed; the equal-weight version
loses to AR(1) by 1.28-2.07x and the NNLS version that "wins" does so on 12 folds with weights that move
every quarter); Google Trends share-of-search as a feature; Eurostat as a nowcast; Inside Airbnb listed
prices (discontinued); Common Crawl as a demand series; the qualitative regional bands as a regression
target; more free-source scraping of the kind Theo's edge-discovery runs already exhausted.

---

## 10. File map and collected corrections

### 10.1 What was produced tonight

**Notes** — `research/notes/overnight/` (15 including this one)

| File | One line |
|---|---|
| `01_data-census.md` | 217 datasets mapped to KPI, point-in-time lag, verdict and untested idea; the five survivors; the 12 gaps; Theo's off-machine priorities |
| `02_kpi-panel-and-guidance-ledger.md` | 24-quarter reconciled KPI panel (119 cols) + a **194-row guidance ledger**, all quotes re-verified; cushion history; 17 reaction tests, all LOO-negative |
| `03_management-language-and-stock.md` | All 23 calls parsed (1,677 turns, 132 features); 948 tests, **zero survive BH**; the credibility scorecard; the five best and five worst reactions with verbatim quotes |
| `04_consensus-and-reaction.md` | **Consensus reconstructed at all 23 prints** with 145 sourced quotes; 97 reaction tests; the 20-day nights-vs-Street drift; current Street numbers |
| `05_macro-outlook-and-transmission.md` | 1,408 macro pairs with two artefact guards; **the lagged revenue-FX mechanism**; four shock episodes; the macro outlook to end-2027; 30/50/20 scenarios; the dated "change our mind" calendar |
| `06_consumer-choice-and-willingness-to-pay.md` | Hotel-vs-Airbnb price gap; **the bedroom-mix decomposition**; hedonic WTP on 2.85m listing-dumps; the fee arithmetic; 1.71m fee-inclusive quotes; five expert calls |
| `07_ops-and-margin-levers.md` | Cash cost per night, 22 quarters, with the **brand-vs-field S&M split**; 22 initiatives scored; 10-company peer benchmark; lever model FY26-28; path-to-40% Monte Carlo |
| `08_altdata-index-and-backtests.md` | **598 point-in-time feature tests** + 42 index backtests; Trends, backlog, Eurostat, Inside Airbnb; three composites, all failing; the 3Q26 nowcast and guide reconciliation |
| `09_stock-behaviour-and-alpha.md` | 218 logged tests: factor models, post-print drift, seasonality, 16 event groups, 21 rule backtests, options, positioning |
| `10_regional-and-segment-decomposition.md` | 23-quarter regional panel reconciling within 1.1pp; XBRL revenue geography; 3,446 benchmark correlations; **regional FX pass-through**; bottom-up 3Q26/4Q26/FY27 |
| `11_competition-supply-and-overlays.md` | Two-player alt-accom share; supply economics and churn; 39 dated competitor events; **AI exposure grid**; regulatory overlay; new-business scenarios |
| `12_valuation-multiple-regime.md` | Multiple history and regime decomposition; 30 time-series + 24 cross-sectional fits; **the exit-multiple recommendation**; lens tracking; print-day attribution; target dispersion |
| `13_driver-model-build.md` | The Excel workbook and Python mirror; the input table; seasonality and FX mechanics; the quarterly path; **17 documented choices where workstreams disagreed** |
| `15_red-team.md` | 98 claims re-derived against primary sources (83 confirmed, 9 wrong, 2 unsupported, 4 unverifiable); 16 cross-note conflicts; all 34 WS01-12 scripts re-run clean |
| **`14_master-synthesis.md`** | **this document** |

**Model** — `model/ABNB_driver_model.xlsx` (9 sheets: Inputs / History / Revenue / Costs / Cash /
Valuation / Street / Card_5Nov / Recon; 2,349 live formulas; scenario selector at `Inputs!$B$4`);
`model/assumptions.md` (section "Overnight run 6-7 Sep 2026", 30 driver rows with sources).

**Scripts** — `analysis/src/overnight/`, **39 files**, each rebuilding its own outputs with `py -3.13`:
`01_data_census.py`; `02_kpi_panel.py`, `02_guidance_ledger.py`, `02_guidance_analysis.py`;
`03_call_features.py`, `03_reaction_tests.py`, `03_forward_claims.py`, `03_event_study.py`;
`04_consensus_at_print.py`, `04_reaction_vs_consensus.py`; `05_macro_transmission.py`;
`06_price_gap.py`, `06_wtp_hedonics.py`, `06_quote_panel.py`, `06_evidence_tables.py`;
`07_cost_lines_per_night.py`, `07_ops_initiatives.py`, `07_peer_benchmark.py`, `07_margin_lever_model.py`;
`08_trends_pull.py`, `08_inside_airbnb_demand.py`, `08_altdata_backtests.py`; `09_stock_behaviour.py`;
`10_fetch_fx.py`, `10_fetch_xbrl_geography.py`, `10_fetch_eurostat_latest.py`, `10_fetch_benchmarks.py`,
`10_regional_panel.py`, `10_benchmarks.py`, `10_regional_forecast.py`;
`11_competition_supply_overlays.py`; `12_abnb_multiples_history.py`, `12_peer_multiples.py`,
`12_exit_multiples_and_targets.py`; `13_driver_model.py`, `13_excel_builder.py`, `13_xlsx_eval.py`;
`15_claim_checks.py`, `15_script_runs.py`.

**Data** — `data/processed/overnight/`, **153 CSVs + 1 JSON**. The ones that matter most:

| File | Why |
|---|---|
| `01_data_census.csv` | 217 rows × 19 cols — the map of everything the team owns |
| `02_guidance_ledger.csv`, `02_guidance_cushion_series.csv`, `02_q3_2026_guide_card.csv` | 194 verified guides; the cushion history; the 3Q26 guide card |
| `02_kpi_panel_quarterly.csv` (24×119), `02_kpi_panel_long.csv` (1,050 rows, 342 verbatim-verified) | The model's historical input table |
| `03_credibility_scorecard.csv`, `03_forward_claims.csv` | 83 forward claims with outcomes; the 62% / 26% / 0-of-7 scorecard |
| `04_consensus_at_print.csv`, `04_consensus_sources.csv`, `04_current_consensus.csv`, `04_reaction_tests.csv` | The consensus series, 145 sourced quotes, today's Street, 97 tests |
| `05_fx_schedule.csv`, `05_fx_fits.csv`, `05_macro_sensitivities.csv`, `05_macro_scenarios.csv` | **The FX schedule — refresh this weekly**; 256 sensitivity rows; the three scenarios |
| `06_price_gap_series.csv`, `06_wtp_hedonic_coefs.csv`, `06_quote_discount_panel.csv` | Hotel-vs-ABNB pricing; hedonic coefficients (n 1.38m); the discount panel (**caveat the schema change**) |
| `07_cost_lines_per_night.csv`, `07_margin_levers_fy26_fy28.csv`, `07_peer_margin_benchmark.csv` | 22 quarters of cash cost per night with the S&M split; the lever model; 10 peers × 5 years |
| `08_feature_tests_all.csv` (598 rows), `08_test_scoreboard.csv`, `08_backlog_tests.csv`, `08_q3_2026_guide_reconciliation.csv` | Every alt-data test; the scoreboard; **both funds-held windows**; the guide reconciliation |
| `09_test_ledger.csv` (218 rows), `09_earnings_drift_stats.csv`, `09_rules_backtest.csv`, `09_implied_vs_realised.csv` | The full test ledger; drift; 21 rules; the options base rate |
| `10_regional_panel_quarterly.csv` (23×79), `10_regional_forecast.csv`, `10_regional_fx_passthrough.csv`, `10_regional_quotes.csv` | The regional build and its reconciliation residual; 766 tagged letter sentences |
| `11_regulatory_overlay.csv`, `11_ai_exposure_scenarios.csv`, `11_new_business_scenarios.csv`, `11_alt_accom_share_quarterly.csv` | The three overlays and the share series |
| `12_exit_multiple_recommendation.csv`, `12_exit_multiple_evidence.csv` (39 rows), `12_price_sensitivity.csv`, `12_peer_multiples.csv`, `12_print_move_attribution.csv` | **The most consequential file set in the run** |
| `13_model_quarterly.csv`, `13_model_annual.csv`, `13_valuation_summary.csv`, `13_scenario_grid.csv` (441 rows), `13_reconciliation.csv` (216 checks, all ok) | The model's outputs and its proof of internal consistency |
| `15_claim_checks.csv` (98), `15_cross_note_conflicts.csv` (16), `15_script_runs.csv` (34) | The audit trail |

**Figures** — `analysis/figures/overnight/`, **24 PNGs**: `02_guidance_cushion`; `03_theme_timeline`,
`03_feature_vs_reaction`, `03_event_study`; `05_fx_mechanism`, `05_macro_vs_nights`,
`05_sensitivity_bars`; `08_indexes_vs_kpis`; `09_earnings_drift`, `09_seasonality`, `09_rolling_betas`,
`09_variance_decomposition`, `09_rules_backtest`, `09_positioning`; `10_regional_nights_growth`,
`10_regional_revenue_mix`, `10_regional_forecast`; `11_alt_accom_growth`; `12_abnb_multiples_history`,
`12_abnb_multiple_drivers`, `12_abnb_lens_tracking`, `12_peer_crosssection`,
`12_exit_multiple_evidence`, `12_analyst_targets`.

*(WS06 and WS07 wrote no figures; WS01, WS04, WS13 and WS15 wrote none by design.)*

### 10.2 Corrections to existing work, collected from every note

**A. Corrections the red team requires (WS15). Apply all of these; none has been edited into the source
notes, per the brief.**

| # | File | Change |
|---|---|---|
| 1 | `01_data-census.md` L19 | "233 point-in-time cells, **zero** beat AR(1)" → **598 cells, 52 beat AR(1), 25 beat both AR(1) and naive — and every one is mechanical FX, not knowable before the print, or window-dependent** |
| 2 | `01_data-census.md` L123 | "2 of 21 indexes" → **17 of 42 rows; FX→ADR at 0.42x is the only one also beating naive by >20%; price→ADR 0.68x** |
| 3 | `01_data-census.md` L16, L137 | Keep "17 of 21" but add: *from the predictive study; on tonight's `04_reaction_tests.csv` the same feature has R² 0.032 and LOO R² −0.18 — a base rate, not a model* |
| 4 | `01_data-census.md` For-the-model | FX slope −0.59 → **−0.715 (n 17, ex-2021, r −0.964)**, the fit WS05 and WS08 both use |
| 5 | `02_*.md` L213 | Nights bucket-guide beat "+3 to +5" → **"+1 to +5 (4Q25 +4.8, 1Q26 +1.2)"** |
| 6 | `03_*.md` L39 | "the only one of 79 features" → **one of only three**, all long-term-target variants; and the −2.31 baseline is itself a badly overfit n=17 model, so the delta is descriptive |
| 7 | `04_*.md` bottom line 4 | "the only positive out-of-sample R² among 97 tests" → **one of nine positive LOO values among 75 LOO-evaluated specs; every positive sits at 20 days, none at day 1** |
| 8 | `05_*.md` L15 | Lagged fit predicts "+2.9pp" → **+2.2pp** (`05_fx_schedule.csv`) against the guided ~+3.0pp — close, and far closer than the contemporaneous −1.6pp, but not exact |
| 9 | `05_*.md` L21, L135 | "fastest nights growth in two years" → **fastest since 4Q24** (+10.3% vs 4Q24's +12.3%) |
| 10 | `06_*.md` L39 | Discount share → **quote-weighted 17.3% (Mar, 10 cities) → 31.4% (Aug, 13 cities); median city 10.9% → 31.4%**, plus the taxes-line caveat (0.20% May → 5.65% Jul → 6.54% Aug) and NYC's 41.5 → 25.3 → 43.5 swing. **Not slide-ready without a matched-listing panel** |
| 11 | `06_*.md` L173 | "about half by 2Q26" → **"over a quarter of active listings" at 1Q26 (disclosed), remainder in migration, complete by year-end** |
| 12 | `06_*.md` L37, L204 | Cleaning-fee line "0.02% of quotes" → **0.006%** |
| 13 | `06_*.md` For-the-model | FY26 take rate "13.2-13.3%, flat vs 2025" → **13.4%, flat vs FY25's actual 13.41%** (13.2-13.3% is a 10-20bp decline, not flat) |
| 14 | `11_*.md` L279, L317 | "+3pts of nights from RNPL" → **+3pts of nights and +4pts of GBV from three features together** (RNPL, cancellation redesign, single-fee migration). The FY27 nights haircut must be smaller than 3pts or explicitly labelled the full three-feature lap |
| 15 | `11_*.md` L26, L312 | "~50% of listings at Q2'26" → **over a quarter at 1Q26 (disclosed), remainder in migration through 2H26** |
| 16 | `11_*.md` L26 + take-rate row | The 6-10% pilot and the −0.8pt impact → keep, flagged **"unverified — the Skift article is paywalled. Do not put −0.8pts in the model until confirmed"** |
| 17 | `12_*.md` L411 | "18.2x NTM EBITDA" → **18.5x**, as in `12_peer_multiples.csv` and section 2 |
| 18 | `12_peer_multiples.csv` ABNB row | `net_cash_musd` 9,569 → **9,593** (XBRL 30 Jun 2026: 6,821 + 5,248 − 2,476; the peer file used total debt 2,496) |
| 19 | `12_*.md` For-the-model | "10y 4.77% (FRED DGS10, 4 Sep 26)" → **3 Sep 26** (the 4 Sep print was not published) |
| 20 | `model/assumptions.md` | Exit multiples 18 / 22 / 25.5x → **13.5 / 16.5 / 18.5x**, with the old grid retained as an explicit "if the market keeps paying 2026 multiples" sensitivity |

**B. Cross-note conflict rulings, with WS13 overriding where its "Choices made" already decided**

| Parameter | Use | Rather than | Note |
|---|---|---|---|
| FY27 revenue growth, base | **+11.3%** (WS13's build) | WS15's arbitration to +12.3%; WS10 +12.4%; WS07 +11.2%; WS05 +10.3% | **WS13 overrides CONF-01** — the model *is* the build, and +11.3% is the consequence of its FX, nights and ADR choices, not an average. Show the others as the range; carry +10.3% as the macro-adverse case |
| FY27 adj. EBITDA margin, base | **35.9%** after the AI referral cost (36.3% before) | WS07's 36.6%; WS05's 36.4% | **WS13 overrides CONF-02.** WS05 is *not* independent corroboration of WS07 — it imports WS07's anchor |
| FY26 revenue, base | **$14.2bn, labelled an above-Street stance** | hiding a 0.5-1.0% gap to consensus | CONF-03 |
| 3Q26 revenue on the card | **$4.78-4.82bn range** | a point estimate | CONF-04; four methods span $4.59-4.83bn |
| 3Q26 ADR FX contribution | **−1.3 to +0.8pp on the card**; **+0.80pp in the model's ADR/GBV display only** | +0.80pp as a point | CONF-05 for the card; WS13 choice #3 for the model (revenue runs off the revenue-FX line, so the display choice does not affect revenue) |
| FX-to-ADR slope, broad USD | **−0.715pp per pt (n 17)** | −0.59 (n 14) | CONF-06 |
| Alt-data features in the forecast | **none** | funds-held as a validated forecaster | CONF-07 |
| Cost of equity / WACC | **10.5%**, band 10.0-11.5% | 10.3% | CONF-08; WS13 choice #10 |
| Mean sell-side target | **$178.96 (46 analysts)** | 179.55 / 179.88 | CONF-09 |
| FY26/FY27 take rate | **~13.4% flat assumed**; the model's *implied reported* 13.45% / 13.25% differs by FX timing, not monetisation | 13.2-13.3% | CONF-10 + WS13's wedge |
| Single-fee coverage at 2Q26 | **"over a quarter at 1Q26, complete by year-end"** | ~50% | CONF-11 |
| FY27 nights haircut for the lap | **labelled the full three-feature lap**, not RNPL alone | −3pts for RNPL | CONF-12 |
| Exit multiple on FY27E EBITDA | **13.5 / 16.5 / 18.5x** | 18 / 22 / 25.5x | CONF-13; WS13 choice #8 |
| Regulatory drag | **EMEA/NA nights drags inside the regional build only** | nights drag AND global revenue drag (double-counts ~0.75% of FY27 revenue) | CONF-14; WS13 choice #13 |
| SBC % of revenue | **state the basis**: 12.92% FY25 on the driver panel (P&L expense), 13.1% in WS07's peer file (cash-flow add-back), 12.9% LTM to 2Q26 | one number without a basis | CONF-15 |
| Nights-acceleration rule | **base rate with its n** | a per-point coefficient | CONF-16; standardise the definition first |

**C. Corrections to pre-existing files found by the workstreams themselves**

- **`data/processed/abnb_valuation_scenarios.csv` overstates net cash.** FY27E base $12,358M never
  subtracted RSU tax withholding ($561M FY2025, ~$688M FY2027). Rolling the 30 Jun 2026 actual ($9,593M)
  forward gives **$10,116M** — about **$4/share** on every EV lens. *(WS13)*
- **The same file sets FY26-28 FCF equal to adjusted EBITDA** (100% conversion). WS07's bridge gives
  **99 / 95 / 92%**; FY2025 actual was 107% and falling as the guest float stops growing. *(WS13)*
- **`2026-09-05_margin-drivers.md` §1.4 and §4 have the 2026 S&M mix backwards.** FY2025 was field ops
  +43% / brand +10%; **1H26 is brand and performance +32% ($1,091M vs $824M) and field ops +24%**. *(WS07)*
- **`abnb_margin_scenarios.csv`'s FY2027 bear is too kind on cost** — it flexes total S&M to +9% in a
  year revenue grows 4.3%, which needs brand spend roughly flat off a +25-32% exit run-rate. *(WS07)*
- **`AdvertisingExpense` in XBRL is not the brand-and-performance line** (FY2025 tags $843M against the
  10-K's $1,595M) and must not be used as one. *(WS07)*
- **`2026-09-05_eu-platform-and-backlog.md`'s "unearned fees R² 0.96 on next-quarter revenue" is
  in-sample only**; walk-forward it is 1.85x AR(1). Describe the backlog as **coincident**. *(WS01, WS08)*
- **`predictive/03_macro-altdata-nowcast.md` finding 1** puts the 3Q26 FX tailwind at "+0.8pp"; the EUR
  fit, which has the higher r, gives **−1.3pp**. Widen to a range. **Finding 2 treats FX-to-revenue as
  the same contemporaneous mechanism as FX-to-ADR. It is not.** *(WS05)*
- **`2026-09-05_abnb-major-moves.md` §2b**: "mean 20-session excess −4.7% across 22 prints" → **−3.6%
  across 23** with 2Q26's window complete (+22.5%). §4.3: ABNB **never** had a significant rates beta in
  any year, including 2022 — phrase it as a long-duration-growth beta falling 1.28 → 0.91. *(WS09)*
- **`abnb_earnings_reactions.csv` has no 20-session row for 2026Q2.** It is **+22.5%** (day-1 +16.8%,
  drift +3.2%). *(WS09)*
- **`data/processed/overnight/10_regional_revenue_xbrl.csv` had a comment as its first line**, so pandas
  read the comment as the header. *(WS01 → WS10)*
- **`06_price_per_unit_panel.csv` renames Inside Airbnb's `estimated_occupancy_l365d`** to
  `mean_est_nights_booked_l365d`: **that field is estimated nights booked in the last 365 days (0-365),
  not an occupancy percentage.** Anything in the repo treating it as a percentage is wrong. *(WS06)*
- **Characterise the AirROI "55.9% median checkout markup" correctly rather than dismissing it**
  (AirROI, 16 Apr 2026). It is a *modelled* 3-night total — `[(market ADR × 3) + median cleaning fee]
  × 1.14 × (1 + lodging tax)` — measured against the nightly subtotal, not observed checkouts; about 31%
  of the markup is lodging tax and 39% is the host-set cleaning fee, neither of which Airbnb keeps; and it
  assumes the pre-migration 14% guest service fee, which no longer applied to about half of active
  listings by 2Q26. It is not evidence about hidden fees, and it does not contradict our parse of 1.71m
  quote responses. *(WS06, corrected by WS16)*
- **`11_competition_supply_overlays.py` had three defects, now fixed and re-run**: a merge-key mismatch
  nulled the BKNG/EXPE columns; the AI-cost percentage was understated **1000x**; and Inside Airbnb
  retention included partial-scope dumps (25 of 103 pairs, averaging 0.489 against 0.726 for the clean
  78 — the un-excluded means implied a supply collapse that was a city-boundary artefact). *(WS11)*
- **WS15's corrections 11 and 15 are withdrawn**: "approximately half of our active listings are now
  subject to the single service fee" is verbatim in the 2Q26 call (Mertz, prepared remarks,
  `data/raw/regulatory/transcripts/2026-Q2.txt`). WS06 and WS11 were right; the figure is absent from the
  letter only. *(WS16)*
- **`research/sources/README.md` reuses S-numbers** — S30, S32-S37 each appear twice. *(WS01)*
- **`theos-past-research/research/transcripts/*.csv` are empty schemas** (`guidance_facts`,
  `reported_metrics`, `management_themes` were never populated). *(WS01)*
- **Two of Theo's `absolute_floor` guidance rows** (2021Q1, 2021Q4, `value_low = 0.0`) encode "positive
  Adjusted EBITDA", not a 0% margin floor. *(WS02)*
- **`data/processed/abnb_options_ledger.csv` exists only in the main tree**, and its
  `event_implied_move_pct` of 0.0 for the Nov-20 expiry reads as a failed calculation — though at 76dte
  the correct answer does happen to be approximately zero. *(WS09)*
- **WS10 weights regional nights growth by the forecast quarter's share rather than the base quarter's**
  (3Q26: +10.29% vs +10.47%), and **adds the FX contribution to GBV growth additively** (13.60 + 3.00 =
  16.60% where compounding gives 17.01%; $19M on 3Q26 revenue). The model uses base-period weights and
  compounding. *(WS13)*
- **WS07's FCF bridge needs an "other income/(expense)" line to tie to FY2025** (without the −$112M it
  produces $4,725M against a reported $4,613M). *(WS13)*
- **`data/processed/predictive/02_peer_prints.csv` carries worldwide, not regional, MAR/HLT RevPAR.** Any
  regional hotel-RevPAR claim needs a new source. *(WS10)*

### 10.3 Reproducibility and licensing

**All 34 WS01-12 scripts were re-run end to end with `py -3.13` and all 34 exited 0.** Only three outputs
moved a byte, all because the script re-fetches live data (`08_trends_weekly.csv` +3 bytes on a fresh
Google pull; `10_regional_benchmarks.csv` −1 byte; `10_xbrl_revenue_geography.csv` 259 → 255 rows on a
fresh EDGAR pull — WS10's *derived* outputs are byte-identical either way). Those three were restored so
notes 01-12 stay consistent with the data they were written on. **The layer is genuinely reproducible.**

**Licensing.** 111 sources public (SEC/company), 32 public domain (FRED/BEA/EDGAR), **20 CC BY 4.0
(Inside Airbnb — attribute on slides)**, 7 Yahoo-terms (do not redistribute), 4 licensed (Third Bridge,
LSEG, FactSet, Bloomberg — do not quote at length), 3 Eurostat re-use (attribute). The red team checked
all twelve notes for quotation from the five Third Bridge PDFs: Third Bridge appears in notes 01, 06 and
11 only, and **no excerpt exceeds ten words**. Nothing needs redacting.

**What could not be verified at all:** CoStar hotel ADR (subscription), the Skift host-fee pilot
(paywall), and Zacks consensus (the notes store verbatim quotes and URLs, which is the right mitigation).
**Not checked by the red team:** WS07's Monte Carlo (only its inputs), WS09's factor regressions (only its
summary statistics), WS12's print-day decomposition, and WS05's full 1,408-pair grid — each recorded as
`unverifiable` rather than confirmed in `15_claim_checks.csv`.

---

## 11. Post-run corrections (WS16, WS17, WS18)

*Three workstreams ran after this note was first written on 7 Sep. Their edits are already folded into
the sections above; this section says what changed and why, so a reader of the 6 Sep version can diff.*

### 11.1 Consensus and the web gaps (WS16)

- **A ninth guide-below-Street print exists.** The 2Q24 next-quarter consensus was **$3,840m (LSEG, via
  Reuters, 6 Aug 2024)** against a $3,700m guide midpoint - a **-3.65% guide-vs-Street**, the largest in
  the sample, attached to the second-worst day-1 move (-12.3%). **Every "8/8" in this note is now "9/9",
  mean -8.90%, base-rate p 0.057** (was 0.078). The day-1 spec strengthens (n 19, R2 0.164, HC1 t +1.82,
  p 0.069) but **stays LOO-negative (-0.149), so the no-day-1-alpha conclusion survives**. The
  nights-drift result is untouched.
- **Three 2021 EPS consensus cells were also recovered, and they are a trap.** Adding them manufactures a
  spurious negative day-1 EPS coefficient (the 2021 GAAP "misses" are IPO stock comp) and kills three of
  WS04's nine positive-LOO specs. Composition of the nine changes: **five at 20 days, four at five days,
  none at day 1**. The clause "every positive sits at 20 days" (red-team correction 7) is no longer true;
  "not one is at day 1" still is.
- **An ADR consensus does exist.** Zacks publishes a "GBV per Night and Experience Booked (ADR)"
  consensus, recovered for five prints (1Q25 $170.55, 3Q25 $166.67, 4Q25 $165.52, 1Q26 $178.54, 2Q26
  $181.56). ABNB has beaten it **5 of 5** by +0.5% to +4.6%; correlation with day-1 on n=5 is **-0.46**.
  WS04's "0 / 23, no publisher quotes one, ever" is withdrawn.
- **Red-team corrections 11 and 15 are withdrawn.** *"Approximately half of our active listings are now
  subject to the single service fee"* is verbatim in the **2Q26 call** (Ellie Mertz, prepared remarks,
  6 Aug 2026, `data/raw/regulatory/transcripts/2026-Q2.txt`). It is absent from the letter only, which is
  why a letter-only check missed it. WS06 and WS11 were right.
- **The direct-booking pilot is verified and the -0.8pt is too big.** Airbnb's own product copy (host
  community forum, 28 Aug 2026) and RSU by PriceLabs (31 Aug 2026) give the mechanics: host fee 15.5% ->
  **6% or 10%** on a host-generated tracked link, invite-only, US, transaction stays on Airbnb. A -0.8pt
  hit to a ~13.4% take rate needs **8.4% of all GBV** at the 6% tier or **14.5%** at the 10% tier. **Use
  0-15bp of FY27 take rate**; reserve -0.8pt for a "pilot becomes policy" tail.
- **AirROI's 55.9% is a model, not a measurement.** `[(market ADR x 3) + median cleaning fee] x 1.14 x
  (1 + lodging tax)` against the nightly subtotal. It includes lodging tax and the host's cleaning fee,
  and it assumes the pre-migration 14% guest fee. Characterise it; do not dismiss it, and do not treat it
  as evidence about hidden fees.
- **Press attribution.** Re-read against contemporaneous coverage, WS03's `driver_class` should read
  **guide 6 / KPI 2 / macro 1 / investment spend 1**, not guide 4 / KPI 4 - which *strengthens* the run's
  claim that ABNB trades on the forward statement. **2020Q4's "margin" attribution has no contemporaneous
  support at all**: every same-day source attributes it to the revenue and gross-bookings beat. Do not
  use 2020Q4 as evidence that long-term margin framing moves the stock. Separately, two sell-side
  upgrades (Baird, Goldman) landed on the morning of the +14.0% 2024Q4 move; no workstream carries
  same-day analyst actions.
- **Calendar.** **Chesky speaks at Goldman Sachs Communacopia + Technology on 8 Sep 2026, 6:05pm ET**,
  public webcast - the only scheduled management appearance before the print. The **9 Sep EU proposal
  leaked on 4 Sep** (Reuters): it devolves capping powers to *member states* in housing-shortage areas
  subject to non-discrimination, proportionality and public-interest tests. An enabling framework, not an
  EU-level cap, and consistent with WS11's 0.18%-of-2027-revenue expected value.
- **For the card:** Zacks publishes nights, ADR and GBV consensus **2-3 days before each print**, so the
  Q3-26 nights bar arrives free on ~2-3 Nov. Expect a 1-2% vendor gap to StreetAccount.

### 11.2 The workbook in real Excel (WS17)

Excel 16.0 was driven over PowerShell COM, the workbook rebuilt with `CalculateFullRebuild()`:
**0 error cells in 5,547**, no circular reference, calculation state `xlDone`, **all 216 named outputs
and all 2,349 formula cells matching the Python mirror** (worst 4.2e-15), and all 216 `Recon` delta cells
reading exactly 0 inside Excel. The arithmetic was right. Sixteen findings on the mechanics around it -
**eleven fixed with no number moving**, of which the two that mattered: **the scenario selector was inert**
(126 `CHOOSE` cells on Inputs were its only consumers; Valuation and Card_5Nov now carry an Active column
driven by `Inputs!B4`, and switching it moves 135/136 cells), and **the reverse-DCF answer was a pasted
offline solve** (now marked as an input with a live staleness check reading 0.00). Numeric literals inside
formulas fell from 121 cells to 3. Left open for a human: the DCF's valuation date (the strip is a value
as of end-FY2027 against a 4 Sep 2026 spot), an Inputs row for the three 5 Sep memo multiples, FY2025
interest expense, and whether the regulatory drag should be quarterly.

### 11.3 The share-count fix (WS18)

WS17's one open high-severity finding: **the FY2026 share roll double-counted the 1H26 buyback.** Both
roll-forwards start from the 30 Jun 2026 actuals (597.0M diluted shares, $9,593M net cash), but the share
line applied the **full-year** buyback and SBC to that count while the net-cash line correctly netted the
1H26 actuals out of every flow. Fixed in `13_driver_model.py` and `13_excel_builder.py` together: FY2026
now consumes only the 2H26 buyback (FY26 less the $2,139M actual) and only 2H26 SBC (FY26 less the $897M
actual), which is exactly the convention the net-cash line uses; FY2027 and FY2028 take the full year.

**FY2026E diluted shares 580.3M -> 588.9M (+8.55M, +1.47%)**, carried into FY2027E (566.0 -> 574.6) and
FY2028E (553.0 -> 561.5). Every per-share number falls ~1.45-1.55% and every one of the six football-field
lenses with it: **base football-field mean $162.65 -> $160.22**, base EV/EBITDA lens $184 -> $181, bear
mean $77 -> $76, bull mean $236 -> $233. Nothing above the share line moved - revenue, margins, EBITDA,
FCF and net cash are identical. The regenerated workbook re-passes everything: 0 Excel errors in 5,547
cells, 216/216 outputs matching, 2,349/2,349 formula cells matching, scenario switch working (143
comparisons, 0 mismatches). Before/after for every affected output:
`data/processed/overnight/18_share_fix_delta.csv`; the full correction ledger:
`18_corrections_applied.csv`; the note: `research/notes/overnight/18_corrections-applied.md`.

---

## For the thesis file

`research/thesis.md` is still the empty template. On tonight's evidence it should be filled as:

- **Recommendation:** the operating case does not support a long at $181.94 on the evidence-based exit
  multiple. Base $181 / football-field mean $160; 25/50/25 weighted $176 on EV/EBITDA, $157 across all
  lenses. **Either the pitch argues FY27 revenue above ~$16.0bn, or SBC below ~10% of revenue, or a
  separately priced optionality bucket — or it is not a long.**
- **Variant perception:** FY27's reported revenue growth is a dollar lap that is already knowable, and
  half of ADR growth is unit size rather than price.
- **Catalysts:** **8 Sep: Chesky at Goldman Sachs Communacopia + Technology, 6:05pm ET, public webcast**
  (Airbnb IR, 25 Aug 2026) — the only scheduled management appearance before the print; 5 Nov Q3 print and
  Q4 guide (the FX bridge is the whole read); 9 Sep EU Affordable Housing Act proposal (headline risk,
  0.18% of 2027 revenue in expectation) — **it already leaked on 4 Sep (Reuters): it devolves capping
  powers to *member states* in housing-shortage areas subject to non-discrimination, proportionality and
  public-interest tests, an enabling framework rather than an EU-level cap**; 8-9 Dec FOMC dots (they set
  the dollar path under our FY27 revenue FX); Feb 2027 FY27 guide.
- **Biggest risk to the thesis, whichever way it points:** the multiple. It is 86% of everything that
  moved tonight.
