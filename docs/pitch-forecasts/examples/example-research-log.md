# RESEARCH LOG

Revision 2 (2026-09-11, after the [September 11 audit](audits/2026-09-11-research-audit.md); changes listed in the [audit response](audits/2026-09-11-audit-response.md)). Revision 1 hash is recorded in [organization-2026-09-11.md](../../organization-2026-09-11.md).

## 0. Metadata
- question_name: usd-iranian-toman-2026-12-31
- question_url: https://www.metaculus.com/questions/45340/
- type: continuous
- run_mode: initial
- run_date: 2026-09-11
- open_date: 2026-09-14
- close_date: 2026-11-30
- resolution_date: 2027-01-01
- scoring: time_averaged
- cp_visible: no
- cp_value: n/a (question upcoming; CP reveal 2026-09-16T17:00Z)

## 0b. Question (verbatim)
### Title
What will be the open market US Dollar/Iranian Toman exchange rate on December 31, 2026?
### Resolution Criteria
NOT YET PUBLISHED (API returned null on 2026-09-11 at 17:0xZ and again at 19:31Z; post status "approved/upcoming"). Range 150,000–250,000 toman, open lower bound, open upper bound, 200 in-range buckets of 500 toman, unit "Iranian Toman". Post ID 45340, tournament metaculus-cup-fall-2026, published 2026-09-11T17:00Z. API payloads saved at [sources/post_45340.json](sources/post_45340.json) and [sources/post_45340_refetch.json](sources/post_45340_refetch.json).
### Fine Print
NOT YET PUBLISHED. **This forecast is conditional on a Bonbast-type open-market source** (Bonbast is the reference used by Polymarket's same-subject markets and by Euronews/Iran International; it quotes toman, 1 toman = 10 rials). A separate 1% probability is assigned to a resolution source that produces a below-range value (e.g. a semi-official rate near 137k). Quote side (sell vs buy), timing and finalization rules are unknown until Sep 14.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Bonbast free-market USD = 234,900 toman on 2026-09-10 (229,100 on 09-08; 235,500 on 09-09); 181,200 on 2026-07-13. Series saved to [datasets/bonbast_usd_toman_2026-07-13_to_09-11.json](datasets/bonbast_usd_toman_2026-07-13_to_09-11.json) (observations end 2026-09-10; filename carries the retrieval date) | https://www.bonbast.com/graph/usd | 2026-09-10 | 2026-09-11 | yes |
| 2 | alanchand USD sell 2,369,000 IRR (buy 2,345,500) on 2026-09-11; 24h range 2,349,500–2,375,000; +6.90% w/w; +49.98% over six months | https://alanchand.com/en/currencies-price/usd | 2026-09-11 | 2026-09-11 | yes |
| 3 | tgju daily USD/IRR closes: 2026-09-10 2,359,750; 09-03 2,210,600; 08-27 2,006,000; 08-17 1,865,000; 07-08 1,801,950; 06-17 1,595,000; 04-08 1,543,400; 2025-12-31 1,355,650; 2025-01-01 806,350 (3,948 daily rows 2011–2026, not every calendar day, saved to [datasets/tgju_usd_irr_history.csv](datasets/tgju_usd_irr_history.csv)) | https://api.tgju.org/v1/market/indicator/summary-table-data/price_dollar_rl | 2026-09-10 | 2026-09-11 | yes |
| 4 | Dollar broke 2.1M rials on Tehran free market Wed 2026-09-02, a record. Euronews writes the rial "lost around 60%" since the Iranian new year when the dollar was ~1.35M; arithmetically 1.35M → 2.1M is a 55.6% rise in the quote (a 35.7% fall in the rial's dollar value). CBI governor: rise "driven more by psychological factors than by real economic factors" | https://www.euronews.com/business/2026/09/02/iranian-rial-hits-record-low-as-us-dollar-breaks-22-million-mark | 2026-09-02 | 2026-09-11 | yes |
| 5 | Rial record low ~2.25M/USD Sat 2026-09-05, ~12.5% weaker since crossing 2M in late Aug; inflation ~66% in July; Bessent plans new secondary sanctions "roughly every week". An appended appliance-industry article on the same page says the struck steel and petrochemical complexes *account for* roughly 50% of steel and 70% of petrochemical capacity; the extent of damage and operating status is reported as unavailable | https://www.iranintl.com/en/202609055912 | 2026-09-05 | 2026-09-11 | yes |
| 6 | CBI governor Hemmati: bank "ready, if necessary, to inject up to $2 billion" (announced capacity, not a verified reserve figure); $500M deployed in the prior week (one week's figure, not a sustained rate); >$18B supplied for essential imports since 2026-03-21; dollar ~2.1M on 2026-08-31 | https://www.iranintl.com/en/202609018792 | 2026-09-01 | 2026-09-11 | yes |
| 7 | Rial ~2.02M/USD on Mon 2026-08-24; June MOU expired 2026-08-17; US sanctioned 60+ targets and expanded sanctionable sectors to digital assets, technology, gold, aviation, shipping; IMF projects 68.9% average 2026 inflation | https://time.com/article/2026/08/24/iranian-rial-hits-record-low-new-us-sanctions/ | 2026-08-24 | 2026-09-11 | yes |
| 8 | War began 2026-02-28 (Khamenei killed); ceasefire/dual blockade 04-08 to 06-19; Islamabad Memorandum signed 06-17; fighting resumed 07-08; August "military lull"; "Renewed hostilities (1 September – present)": US strikes on IRGC targets and NIOC tankers 09-01, Vance says contact cut 09-03, US destroyed five Iranian tankers 09-09, Iran fired 20 missiles intercepted over Jordan 09-09 | https://en.wikipedia.org/wiki/2026_Iran_war | 2026-09-11 | 2026-09-11 | yes |
| 9 | 60-day MOU negotiation window ended 2026-08-17 with no talks begun; Iran: US "began violating the memorandum shortly after its June 18 signing"; Hormuz commodity transits fell to 0–5/day mid-Aug | https://www.cbsnews.com/live-updates/us-iran-war-deal-expired-strait-of-hormuz/ | 2026-08-18 | 2026-09-11 | no |
| 10 | Trump 2026-09-10: war "will end immediately after our election" (Nov 3 midterms); "We're not looking for [talks], to be honest" (search snippet, page not fetched) | https://www.globalsecurity.org/military/ops/iran-war-oprep.htm | 2026-09-10 | 2026-09-11 | no |
| 11 | Reuters (via Al-Monitor), 2026-09-01: Iran loaded about 220,000–255,000 bpd of crude and condensate in August (Vortexa, Kpler), down from ~740,000 bpd in July and ~2M bpd in March; Vortexa: even in 2019–20 some crude cleared Hormuz every month; Kpler's Falakshahi: the collapse "is draining one of Iran's main sources of foreign-currency income and could force Tehran to finance spending by printing money" | https://www.al-monitor.com/originals/2026/09/blockade-succeeds-where-sanctions-failed-iran-oil-exports-stall | 2026-09-01 | 2026-09-11 | yes |
| 12 | Polymarket "USD x Iranian rials End of December?" (Bonbast Dec 31), CLOB midpoints at 2026-09-11T19:32Z: <2.0M 0.155 (bid .15 × 933 / ask .16 × 185); 2.0–2.5M 0.215 (.21 × 76 / .22 × 10); 2.5–3.0M 0.095 (.09 × 5 / .10 × 99); 3.0–3.5M 0.305 (.30 × 80 / .31 × 48); 3.5–4.0M 0.123 (.089 × 20 / .157 × 43); ≥4.0M 0.0405 (.011 × 150 / .07 × 41). Midpoints sum to 0.934; total volume ≈ $9.4k. Books saved to [sources/polymarket_rials_books_20260911T193202Z.json](sources/polymarket_rials_books_20260911T193202Z.json) | https://polymarket.com/event/usd-x-iranian-rials-end-of-december | 2026-09-11 | 2026-09-11 | yes |
| 13 | Polymarket "End of September? (Higher Strikes)" (Bonbast Sep 30), midpoints 19:32Z: <2.2M 0.11; 2.2–2.5M 0.375 (bid .31 / ask .44); 2.5–2.8M 0.355 (.34/.37); 2.8–3.1M 0.086; ≥3.1M 0.0595. Lower-bracket complement P(≥2.5M on Sep 30) = 0.515. Base event ≥2.2M 0.905 ($23k vol) | https://polymarket.com/event/usd-x-iranian-rials-end-of-september-higher-strikes | 2026-09-11 | 2026-09-11 | yes |
| 14 | Polymarket (fetched 2026-09-11T18:59Z, last-trade prices): US x Iran diplomatic meeting by Dec 31 0.375; final nuclear deal by Dec 31 0.105; Iran leadership change by Dec 31 0.145; regime fall before 2027 0.075; Reza Pahlavi head of state end-2026 0.03; Mojtaba Khamenei head of state end-2026 0.85 | https://gamma-api.polymarket.com/public-search?q=Iran%20regime | 2026-09-11 | 2026-09-11 | yes |
| 15 | Metaculus post 45340: numeric, range_min 150000, range_max 250000, open_upper_bound true, open_lower_bound true, open 2026-09-14T17:00Z, close 2026-11-30T23:00Z, resolve 2027-01-01T23:00Z, cp_reveal 2026-09-16T17:00Z; resolution_criteria/fine_print null at 17:0xZ and 19:31Z | https://www.metaculus.com/api/posts/45340/ | 2026-09-11 | 2026-09-11 | yes |
| 16 | Polymarket rial markets resolve on "finalized free-market USD exchange rate ... on Bonbast (https://www.bonbast.com/graph/usd), which publishes prices in Iranian toman"; boundary values go to the higher bracket. Same subject as 45340, not the same contract | https://gamma-api.polymarket.com/public-search?q=Iranian%20rials%20End%20of%20December | 2026-09-11 | 2026-09-11 | no |
| 17 | Trading Economics USDIRR 1,374,600 on 2026-09-11 "unchanged" — semi-official series, not the open market; ZERO WEIGHT (illustrates the source-mismatch risk in 0b) | https://tradingeconomics.com/iran/currency | 2026-09-11 | 2026-09-11 | no |
| 18 | Dollar surpassed 2M rials 2026-08-23; Dec 2025 record low 1.42M; 2025 opened at 817,500 | https://en.wikipedia.org/wiki/Iranian_rial | 2026-09-09 | 2026-09-11 | no |
| 19 | Fixed-horizon base rates from claim 3. Method: for each observation date, terminal value = last quote on or before date+111 calendar days; 90 days of prior history required; log returns; sample SD; nearest-rank quantiles; P(>250k) = share of windows with log return > ln(250/235) = 0.0619. All windows (n=3,805): mean +0.101, sd 0.170, p5 −0.115, p50 +0.064, p95 +0.409, P(>250k) 0.505, P(<0) 0.273. Crisis = trailing 90-day simple quote rise >25% (n=599): mean +0.117, sd 0.247, p5 −0.260, p50 +0.100, p95 +0.604, P(>250k) 0.569, P(<0) 0.327. Same with log>0.25 (=+28.4%, n=490): P(>250k) 0.576. Period restriction (simple>25%): start ≥2018 P(>250k) 0.542 (n=487), ≥2020 0.547 (n=318), ≥2023 0.510 (n=202). Windows overlap; they form ~8 distinct episodes (2012, 2018, 2020, 2022–23, 2024–25, 2025-09/10, 2025-12, 2026-01/03) | computed from claim 3 | 2026-09-11 | 2026-09-11 | yes |
| 20 | Event study (20-calendar-day post-event minimum of the quote vs the last close on/before the event date): 2026-04-08 ceasefire −4.3% (day 10); 2026-06-17 memorandum −1.9% (day 1); 2026-02-27/28 war start −13.1% (day 17, baseline 02-26 close); 2018-08-01 Hemmati appointment −20.5% (day 5); 2023-02-20 −10.8% (day 19). These are selected post-event minima, not causal estimates. Fixed-horizon extremes (separate): largest 111-day quote decline in the series is −39.7% from 2018-09-25 to 2019-01-14 (log −0.506), larger than the −36.2% needed to reach 150k from 235k; unconditional frequency of a 111-day decline ≥15% is 2.5% of windows, ≥20% 1.2%, ≥25% 0.4%, ≥36% 0.03% (all 2018). All percentages are changes in the toman-per-dollar quote | computed from claim 3 | 2026-09-11 | 2026-09-11 | yes |
| 21 | Realized volatility from claim 3, method: zero-mean squared log changes between consecutive observations divided by the calendar-day gaps, annualized ×365: 30d 0.30 (23 obs), 60d 0.27 (48), 90d 0.31 (71), 180d 0.33 (143), 365d 0.33 (297). Implied 111-day sd from 90d vol = 0.17; crisis-sample sd = 0.25. Drift: +6.5%/wk log since 09-03, +6.9%/wk since 08-17, +2.95%/wk since 07-08, +1.9%/wk since 04-08 | computed from claim 3 | 2026-09-11 | 2026-09-11 | yes |
| 22 | Kalshi has no rial/toman series (Economics category scan: only KXIRANCPI, KXIRANCRUDE, KXOFAC, KXIRANIMPORTS) | https://api.elections.kalshi.com/trade-api/v2/series?category=Economics | 2026-09-11 | 2026-09-11 | no |
| 23 | No prior Metaculus question on the rial/toman/bonbast exists (API search "Iranian Toman", "bonbast", "rial") | https://www.metaculus.com/api/posts/?search=bonbast | 2026-09-11 | 2026-09-11 | no |
| 24 | Final 72h check 2026-09-11: tit-for-tat strikes continue; oil >$100 first time since July; IRGC threatens 20-target retaliation; no talks announced | https://www.nbcnews.com/iran | 2026-09-11 | 2026-09-11 | no |
| 25 | IranWire: dollar 234,190 toman in early trading Thu 2026-09-10, 234,740 at 2:37 PM | https://iranwire.com/en/news/157439-iranian-rial-hits-record-low-against-us-dollar/ | 2026-09-10 | 2026-09-11 | no |
| 26 | The 2018 rally (claim 20) followed the appointment of Hemmati as CBI governor and the reopening of licensed exchange houses / secondary market, with no sanctions relief (US sanctions were re-imposed Aug and Nov 2018). Used to justify that policy/sentiment reversals, not only deals, can produce >20% appreciation (training knowledge; consistent with the series) | training | unknown | 2026-09-11 | yes |

## 2. Query Log
1. Iran toman dollar exchange rate today
2. Iranian rial open market rate September 2026
3. Iran news latest
4. [Polymarket public-search] Iran rial
5. [Polymarket public-search] toman
6. [Polymarket public-search] Iran ceasefire
7. [Polymarket public-search] Iran regime
8. [fetch] bonbast.com (values not rendered)
9. [Metaculus API] /api/posts/45340/
10. [fetch] alanchand.com/en/currencies-price/usd
11. [fetch] tradingeconomics.com/iran/currency
12. [fetch] euronews 2026-09-02 rial article
13. [fetch] en.wikipedia.org/wiki/Iranian_rial
14. [fetch] en.wikipedia.org/wiki/2026_Iran_war
15. Iran rial currency this week
16. Iran US talks ceasefire September 2026
17. [Metaculus API] search "Iranian Toman"
18. [Kalshi API] series?category=Economics (grep iran/rial)
19. [tgju API] price_dollar_rl summary-table-data (asc, desc; full paginated history 3,948 rows)
20. [fetch] alanchand page raw HTML (history table not embedded)
21. [fetch] iranintl.com/en/202609055912
22. [fetch] time.com 2026-08-24 rial article
23. [fetch] en.wikipedia.org/wiki/2026_Iran_war_ceasefire (stale, ends June)
24. [fetch] cbsnews live-updates us-iran-war-deal-expired (stale, Aug 18)
25. Iran central bank dollar rate policy intervention
26. Iran rial outlook end of 2026 analysts
27. Iran oil exports blockade sanctions September 2026
28. [Polymarket public-search + CLOB books] Iranian rials End of December / End of September / US x Iran Effective Ceasefire
29. [fetch] Wikipedia raw wikitext 2026_Iran_war (September section) and 2026_Iran_war_ceasefire (no Aug/Sep entries)
30. [Metaculus API] search "bonbast", "rial"
31. [fetch] iranintl.com/en/202609018792
32. [fetch] abcnews live updates (latest entry Sep 6)
33. Iran United States strikes talks September 10 2026
34. Iran currency rial news
35. [fetch] bonbast.com/graph/usd (embedded 60-day series parsed, saved to [datasets/bonbast_usd_toman_2026-07-13_to_09-11.json](datasets/bonbast_usd_toman_2026-07-13_to_09-11.json))
36. Iran news today (final 72-hour neutral recency check — result: strikes continue, oil >$100, no talks; nothing that changes the number)
37. Iran dollar rate Tehran market Thursday Friday
38. [revision 2] [Metaculus API] /api/posts/45340/ refetch 19:31Z (criteria still null)
39. [revision 2] [Polymarket CLOB] book + midpoint for every open rial bracket, saved with timestamp
40. [revision 2] [fetch] usnews.com Reuters copy (timeout); cnbc.com 2026-08-28 (403); al-monitor.com 2026-09-01 (success, claim 11)
41. [revision 2] recomputation of claims 19–21 with explicit definitions and period sensitivity

## 3. Leading Hypothesis Entities
Bonbast, Iranian rial, toman, US naval blockade, Operation Economic Outcast, Scott Bessent, Central Bank of Iran, Hemmati, Strait of Hormuz, Trump

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Rate ends inside 150–250k because a ceasefire, deal, or policy reversal triggers a large rally (>20%) | kept as minority (B+D = 24%) | April and June 2026 ceasefire/MOU produced only 2–4% rallies with the blockade in place (claim 20); the 2018 −40% rally shows a policy/sentiment reversal without sanctions relief can do it (claims 20, 26); such 111-day declines occur in ~1% of windows unconditionally |
| Central bank intervention holds a plateau near current levels through Dec | kept as minority (A2 17%) | one week of $500M and an announced $2B capacity (claim 6) against export earnings that fell to ~240k bpd (claim 11); 2012 and 2020 peaks were followed by months of stabilization, so a plateau is a real branch, not a negligible one |
| Question resolves below 150,000 | tail (2.5% = 1% source mismatch + 1.5% economic) | needs a −36% move; happened once in 15 years (2018) at 0.03% of windows unconditionally; the mixture's 1.5% is deliberately heavier than that because the current regime is more extreme than the sample |
| Trading Economics 1.37M series is the "open market" rate | discarded as the economic source; retained as the source-mismatch risk | flat semi-official series; the title says "open market" |
| Hyperinflationary blow-off to >4M rials (400k toman) by Dec 31 | kept as tail (8% >400k) | needs ~+55% log in 16 weeks; the 2018 crisis reached p95 = +0.67 in crisis windows |
| Polymarket Dec bracket shape (30.5% on 3.0–3.5M vs 9.5% on 2.5–3.0M) is informative | discarded as shape; bound split retained | depth only in the two lowest brackets; the coherent anchor is the lower-bracket complement (claim 12) |
| Question closes Nov 30 so the rate at close is what matters | discarded | resolution is the Dec 31 value; the final standing forecast carries 31 days of unhedged uncertainty (see section 8, Nov 29 rows) |
| September pace (6.5%/wk) persists to Dec 31 | kept inside A1/C tails, not as the central path | 235k × 1.06^16 = 597k; blow-off phases in this series (2012-10, 2018-09, 2020-10) lasted 3–8 weeks before stabilizing or reversing |

## 5. Independent Estimates
- base_rate_estimate: P(>250k) = 0.57 (range 0.51–0.58 across crisis definitions and start-year restrictions; ~8 episodes), median 259k, 5–95% 181k–430k — S0 235k × crisis-window 111-day log-return distribution (claim 19)
- decomposition_estimate: median 257k, 5–95% 175k–438k, P(>250k) = 0.549, P(<150k) = 0.025 — scenario mixture in log space: A1 no-deal erosion 48% (mu +0.20, sd 0.20), A2 plateau 17% (+0.03, 0.09), B policy/sentiment reversal or talks 20% (−0.10, 0.13), C acceleration 11% (+0.55, 0.25), D blockade lift/regime change 4% (−0.35, 0.25); plus 1% source-mismatch mass below the range; evaluated analytically (normal-mixture CDF), reproduced by the audit script within rounding
- anchor_estimate: P(≥250k) = 0.63 (spread interval 0.62–0.64) from the lower-bracket complement of the Polymarket December midpoints; raw upper-bracket sum 0.57 and proportional normalization 0.61 recorded as alternative repairs; implied median in the 3.0–3.5M bracket under normalization, but that bracket has no depth
- anchor_value: P(>250,000 toman) = 0.63 (Polymarket, coherent repair, 2026-09-11T19:32Z)
- final_estimate: median 257k; P(>250k) = 0.55; P(<150k) = 0.025; percentiles 5/10/25/50/75/90/95 = 175k/194k/223k/257k/314k/383k/438k
- final_minus_anchor: −8 pts on P(>250k). Justification for the divergence: (1) the market's 21.5% on 200–250k under-weights post-peak stabilization, which ends one-third of historical crisis windows with the rial stronger and which the CBI is actively attempting; (2) the base rate restricted to 2018+ or 2020+ is 0.54–0.55 and to 2023+ is 0.51; (3) the market's depth is ~$1k on the two brackets that determine the complement. NOT_INDEPENDENTLY_DERIVED flag is not applicable at 8 points, but note that the base-rate and decomposition estimates share the tgju series and that the market was read before the mixture was finalized; the three numbers are not independent draws

## 6. Final Numbers
| Percentile | Toman per USD |
|---|---|
| 5 | 175,000 |
| 10 | 194,000 |
| 25 | 223,000 |
| 50 | 257,000 |
| 75 | 314,000 |
| 90 | 383,000 |
| 95 | 438,000 |
Mass below lower bound (150,000): 2.5% (1.0% source mismatch + 1.5% economic)
Mass above upper bound (250,000): 55%
In-range mass: 42.6% (9.9% in 150–200k, 32.7% in 200–250k)
Modes: unimodal in range with the in-range density maximum at ≈237,700 toman; scoring density ≥ 0.054 everywhere in range (floor 0.01)
P(>400k): 8.1%
Exported CDF: [forecasts/2026-09-11-prepared-cdf.json](forecasts/2026-09-11-prepared-cdf.json) — 201 points on the 150k–250k grid, every step ≥ 5×10⁻⁵, cdf[0] = 0.0247, cdf[200] = 0.4511. **Prepared, not submitted.**

## 7. Sensitivity
All rows recomputed with the update procedure defined in section 8 (re-center spot; scale drift by T/111 and SD by √(T/111); explicit weight transfers).
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| No blockade lift before Dec 31 (A1+A2+C = 76%) | blockade lifted (A1 12, A2 8, B 35, C 5, D 40): median 209k, P(>250k) 0.22, P(<150k) 0.15 |
| Talks do not start (B = 20%) | direct talks announced (A1 48→38, A2 17→12, B 20→35): median 246k, P(>250k) 0.47 |
| Plateau is a minority branch (A2 = 17%) | 2012-style plateau dominant (A1 30, A2 35): median 248k, P(>250k) 0.48 |
| A1 drift +0.20 log over 111 days (≈1.3%/wk) | A1 drift = September pace (+0.90 log): median 418k, P(>250k) 0.665, P(>400k) 0.52 |
| Spot at open (Sep 14) ≈ 235k | spot +5% (247k, T=108): P(>250k) 0.635, median 269k; spot −5% (223k): P(>250k) 0.46, median 244k |
| Resolution source is Bonbast-type (99%) | source-mismatch risk 5% instead of 1%: P(<150k) 0.065, P(>250k) 0.53 |

## 8. Monitoring Calendar
Update procedure (used for every row): (a) S0 = latest Bonbast close; (b) remaining horizon T = days to Dec 31; each component keeps its weight, drift mu×T/111, SD sd×√(T/111); (c) event triggers transfer weight between named components as listed; (d) source-mismatch mass stays 1% until criteria are published, then 0% or a re-estimated value.
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-14 17:00Z | Question opens; resolution criteria/fine print published | Confirm source, quote side, finalization rule; set source-mismatch mass; re-center S0; enter forecast. Reference values: spot 235k → P(>250k) 0.55; 247k → 0.635; 223k → 0.46 |
| 2026-09-16 17:00Z | CP reveal | If CP's above-bound mass < 40% and spot ≥ 235k: hold 55% (named asymmetry: range set before the September move; anchor 63%). If CP ≥ 55%: hold. Do not exceed 0.63 without new evidence |
| 2026-09-30 | Polymarket End-of-September Bonbast markets resolve | Bonbast ≥ 250k (T=92): P(>250k) 0.65, median 269k. Bonbast ≤ 225k: P(>250k) 0.44, median 242k. Weights unchanged either way |
| weekly (Sun) | Bonbast close vs prior week | Apply (a)–(b); no weight change on price alone. Ignore single-day prints >5% until confirmed by the next close |
| any date | Direct US–Iran talks announced or mediator-hosted meeting scheduled | A1 48→38, A2 17→12, B 20→35: P(>250k) −8 pts, median −4% |
| any date | Blockade lifted / Hormuz reopened by agreement / MOU-style signing | A1 12, A2 8, B 35, C 5, D 40: median ≈ 209k, P(>250k) ≈ 0.22 — apply within hours |
| any date | CBI leadership change or exchange-market liberalization (2018 analog) | B 20→30 from A1: P(>250k) −5 pts; re-evaluate after two weekly closes |
| any date | New OFAC package / reserve news | no weight change unless the weekly close moves >5% |
| 2026-11-03 | US midterms (Trump: war "will end immediately after our election") | no pre-emptive change; apply the talks/blockade rules if events follow |
| 2026-11-29 | Last update before close (Nov 30 23:00Z), T=32 | Apply (a)–(b) only. Reference: spot 230k → P(>250k) 0.29, median 236k; 260k → 0.75, median 267k; 300k → 0.97, median 308k |


## 10. Verification note — 2026-09-12 (Metaculus comment claim: "Tejarat News, 9 Sep: analysts see 240–250k by late Dec, 250–300k by Mar 2027; CBI bought ~$4.5B at lower levels and will engineer a correction to 200–205k")

Checked against the primary sources. The claim merges three separate items and overstates the central bank's role.

| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 30 | Tejarat News, analyst Arad Pourkar: "until the end of autumn the 240–250k corridor is foreseeable"; "the dollar CAN correct to 200–205k, and if it reaches that range one can deploy the second tranche of capital" (a two-tranche buy strategy, NOT a CBI target); "per information presented, ~$4.5B has been added to CBI FX assets"; likens CBI behaviour to 2018–2020 reserve accumulation at lower prices | https://tejaratnews.com/مقصد-بعدی-قیمت-دلار-۲۵۰-هزار-تومان-است | 2026-09-09 (18 Shahrivar 1405) | 2026-09-12 | no |
| 31 | Tejarat News, analyst Milad Zamani: "the 250–270k corridor could apply by year-end" (Iranian year-end = 20 Mar 2027); CBI short-term policy "can temporarily slow the rise"; unlikely to hold below 200k | https://tejaratnews.com/سناریوی-جدید-برای-دلار-دلار-۲۵۰-تا-۲۷۰ | 2026-09-01 | 2026-09-12 | no |
| 32 | CBI official clarification: the $4.5B is FX bought from the domestic market / mopping up excess supply (export repatriation), "not new resources from oil or external sources"; separately $1.4B added to banknote reserves. No statement of a target rate or intent to push the rate down | https://ecoiran.com/بخش-بانک-152/150178 (also ibena.ir/fa/news/186025) | 2026-08-22 (31 Mordad 1405) | 2026-09-12 | yes |
| 33 | Tejarat News, analyst Hatef Shamloo: dollar fell 229k→223k on Hemmati's $2B supply signal; 222k support, further correction to 210–212k "possible with positive news"; year-end dollar "can be the 30 corridor" (300k) | https://tejaratnews.com/اصلاح-قیمت-دلار-و-طلا-موقتی-است-قیمت-طل | 2026-09-07 | 2026-09-12 | no |

Findings:
- "240–250k by late December": real, one analyst (Pourkar), horizon "end of autumn" (~21 Dec). "250–300k by March 2027": a blend of Zamani (250–270k) and Shamloo (300k), both Iranian-year-end (20 Mar 2027). None of the three is a CBI statement.
- "CBI will engineer a correction to 200–205k": NOT supported. Pourkar says the rate *can* correct to 200–205k and frames it as a buy-the-dip level. The CBI's own line (claim 32, Aug 22) is only that it accumulated $4.5B by buying domestic excess supply; the stated policy is Hemmati's "$2B injection capacity" (claim 6). No CBI target level exists in any source found.
- "$4.5B bought at lower levels": partly true. The purchases predate Aug 22, when the rate was ~190–200k, so they were at lower levels than today; but it is reserve accumulation from repatriated export FX, not a war chest announced for pushing the rate to 200–205k.
- Net effect on the forecast: none. The A2 "CBI plateau" branch (17%) already carries the $2B capacity and the 2012/2020 post-peak stabilisation analogs; these sources add analyst opinion, not policy. The 200–205k buy-the-dip talk among Tehran analysts is, if anything, evidence that a dip would meet demand, which supports the >250k branch rather than the 200–250k bracket. Hold P(>250k) ≈ 55%.
- Monitoring: tejaratnews.com daily "پیش بینی قیمت دلار" pieces are a good same-day read on market-maker (بازارساز) behaviour; the useful trigger remains an explicit CBI statement of a rate target or a change in the $2B injection language (claim 6), not analyst corridor calls.
