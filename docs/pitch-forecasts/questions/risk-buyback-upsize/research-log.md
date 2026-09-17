# RESEARCH LOG

## 0. Metadata
- question_name: risk-buyback-upsize
- question_url: n/a (internal pitch-forecast question R06, `docs/pitch-forecasts/QUESTIONS.md`)
- type: binary
- run_mode: initial
- run_date: 2026-09-17
- open_date: 2026-09-16
- close_date: 2027-02-11
- resolution_date: 2027-02-11
- scoring: spot
- cp_visible: no
- cp_value: n/a
- revision: 1
- agent: fable
- batch: A11 (with R08 and R09)

## 0b. Question (verbatim)
### Title
Will Airbnb announce a new share repurchase authorization of ≥ $5bn, or repurchase ≥ $1.5bn in a single quarter (4Q26), by the Feb print?
### Resolution Criteria
**Type.** Binary. **Resolution.** Yes on either a board authorization ≥$5bn announced 17 Sep 2026–Feb print, or 4Q26 repurchases ≥$1.5bn per the 4Q26 letter/10-K. Resolution ~11 Feb 2027.
### Fine Print
(none in the registry.) Conventions adopted here and forecast under:
1. The window runs from 17 Sep 2026 through the 4Q26 shareholder letter and call inclusive (an authorization announced in the 4Q26 letter counts; Airbnb has only ever announced authorizations inside the letter, claim 3).
2. "New authorization ≥$5bn" = a board-approved new program or increase whose own size is ≥$5.0bn ("an additional $6 billion" counts on the $6bn; a $3bn top-up does not, whatever the resulting total capacity).
3. "4Q26 repurchases" = the dollar figure the 4Q26 letter gives for the quarter ("During Q4 2026, we repurchased $X of our Class A common stock"); if the letter is silent, the 10-K cash-flow line for the quarter. An accelerated share repurchase counts at notional in the quarter it is executed.
4. Either leg resolves Yes; the two legs are correlated (a November authorization raises the chance of a heavier Q4) and are modelled jointly.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Four authorizations to date, all announced in the shareholder letter on a print day: $2.0bn (2 Aug 2022, 2Q22 letter, first program), $2.5bn (9 May 2023, 1Q23 letter, prior program fully used), $6.0bn (13 Feb 2024, 4Q23 letter, $750M of prior remaining), "additional $6 billion" (6 Aug 2025, 2Q25 letter, $1.5bn of prior remaining) | data/raw/letters/2Q22_d353427dex991.htm; 1Q23_d453262dex991.htm; 4Q23_d646462dex991.htm; 2Q25_d17531dex991.htm (regex extraction, query 3); datasets/authorization_history.csv | 2022-08-02 to 2025-08-06 | 2026-09-17 | yes |
| 2 | Remaining capacity at each print (letters): 3Q22 $1.0bn, 4Q22 $0.5bn, 1Q23 $0, 2Q23 $2.0bn, 3Q23 $1.5bn, 4Q23 $0.75bn, 1Q24 $6.0bn, 2Q24 $5.25bn, 3Q24 $4.2bn, 4Q24 $3.3bn, 1Q25 $2.5bn, 2Q25 $1.5bn (+$6bn new), 3Q25 $6.6bn, 4Q25 $5.6bn, 1Q26 $4.5bn, 2Q26 $3.4bn | datasets/print_state_panel.csv (from the letters, query 3) | 2022-11-01 to 2026-08-06 | 2026-09-17 | yes |
| 3 | Airbnb has never made an off-cycle capital-return announcement; all four authorizations were inside the letter, so the event-study cannot measure a buyback effect (abnormal returns indistinguishable from zero) | research/notes/overnight/09_stock-behaviour-and-alpha.md §6 | 2026-09-07 | 2026-09-17 | yes |
| 4 | EDGAR submissions index: every 8-K with items 2.02/9.01 since 2023 is a print day; off-cycle 8-Ks are 5.07 (AGM), 5.02 (officers), 8.01 (7 Nov, 14 Nov, 13 Dec 2023) and 16 Mar 2026 (1.01/2.03/8.01, the $2.5bn notes). No off-cycle 8-K announces a repurchase program | https://data.sec.gov/submissions/CIK0001559720.json ; sources/edgar_submissions_CIK0001559720_20260917T034243Z.json | 2026-09-17 | 2026-09-17 | no |
| 5 | Quarterly repurchases (USD m): 3Q22 1,000; 4Q22 500; 1Q23 493; 2Q23 507; 3Q23 500; 4Q23 752; 1Q24 750; 2Q24 749; 3Q24 1,093; 4Q24 838; 1Q25 807; 2Q25 1,010; 3Q25 877; 4Q25 1,095; 1Q26 1,088; 2Q26 1,051. Maximum single quarter $1,095M; last four quarters $0.88–1.10bn | data/processed/abnb_capital_return_quarterly.csv (buybacks_musd); data/processed/abnb_driver_history_quarterly.csv | 2026-08-06 | 2026-09-17 | yes |
| 6 | Quarter-on-quarter step-ups of ≥40% in the buyback have happened twice in 15 transitions (3Q23→4Q23 +50%, 2Q24→3Q24 +46%); a $1.5bn Q4 needs +37–43% on the 2Q26/4Q25 pace | computed from claim 5 | 2026-09-17 | 2026-09-17 | yes |
| 7 | No opportunistic step-up after sell-offs: after the −8.0% 7 Aug 2025 print the 3Q25 buyback fell to $877M from $1,010M; after the −6.15% 3 Feb 2026 AI scare the 1Q26 buyback was $1,088M vs $1,095M | claim 5; research/notes/overnight/09_stock-behaviour-and-alpha.md §6 named events | 2026-09-07 | 2026-09-17 | yes |
| 8 | 2Q26 letter: "During Q2 2026, we repurchased $1.1 billion ... As of June 30, 2026, we had the authorization to purchase up to $3.4 billion"; capital allocation priorities "organic growth, strategic acquisitions or partnerships, and return of capital to shareholders, in that order" | data/raw/letters/2Q26_d70413dex991.htm | 2026-08-06 | 2026-09-17 | yes |
| 9 | Balance sheet 30 Jun 2026: $12.1bn cash, equivalents, short-term investments and restricted cash; $12.2bn funds held; long-term debt $2,476M; $2.5bn senior notes issued March 2026 (of which $2.0bn repaid the 2026 converts, ~$500M retained) | data/raw/letters/2Q26_d70413dex991.htm; data/raw/regulatory/quantification/abnb_2026q2_10q.html | 2026-08-06 | 2026-09-17 | no |
| 10 | FY26 FCF $4.4–4.8bn (bias-adjusted $4,445M, mid $4,844M); FY27 $4.9–5.3bn; quarterly FCF not forecast (M7 failed); 4Q FCF is the seasonal low (4Q25 $521M, 4Q24 $458M) | docs/margin-build/SYNTHESIS.md §3; data/processed/abnb_capital_return_quarterly.csv | 2026-09-15 | 2026-09-17 | yes |
| 11 | Program size vs trailing FY FCF: $2.0bn/3.4 = 0.59x (2022), $2.5bn/3.4 = 0.74x (2023), $6.0bn/3.8 = 1.58x (2024), $6.0bn/4.5 = 1.33x (2025); a $5bn program on FY26 FCF $4.4–4.8bn is 1.05–1.14x, $6bn is 1.25–1.36x | datasets/authorization_history.csv (FCF from claim 5's source, fcf_musd_ltm) | 2026-09-17 | 2026-09-17 | yes |
| 12 | Trigger arithmetic: at the 5 Nov print remaining ≈ $3.4bn − 3Q26 pace (≈$2.3bn, ~2.2 quarters of pace); at the Feb print ≈ $1.2–1.3bn (~1.1–1.3 quarters). Historical announcements came at 0, 1.0–1.2 and 1.5–1.6 quarters of pace remaining; non-announcements at 0.7 and 1.0 (2022–23, when the program was allowed to run out) and at every reading ≥2.7 | datasets/print_state_panel.csv; datasets/r06_model.py | 2026-09-17 | 2026-09-17 | yes |
| 13 | Team's market-implied model holds buybacks at $1,050M a quarter, "which exhausts the $3.4bn authorisation by 2Q27, so a new programme is the likely 4Q26 or 1Q27 announcement" | research/notes/2026-09-13_market-implied-model.md (inputs paragraph) | 2026-09-13 | 2026-09-17 | no |
| 14 | Team FY27 path already assumes continued buybacks: diluted shares 595.8m FY26 → 573.0m FY27 (line build), 570.7m end-FY27 (reverse DCF, after $6.3bn of buybacks) | docs/margin-build/SYNTHESIS.md §3 annual table; research/notes/2026-09-13_market-implied-model.md | 2026-09-15 | 2026-09-17 | yes |
| 15 | Memo risk 6 already frames the buyback as "a floor on sell-offs, not a catalyst" | deck/drafts/memo_v2_short_2026-09-16.md, Risks item 6 | 2026-09-16 | 2026-09-17 | no |
| 16 | Newsroom to 14 Sep 2026: no capital-return item, no Q3 results date; last items are the housing accelerator (14 Sep) and Rijvers as CBO (1 Sep) | https://news.airbnb.com/ | 2026-09-14 | 2026-09-17 | no |
| 17 | No Polymarket or Kalshi market on Airbnb capital return (Polymarket: closed 2Q26 GBV ladders and price-hit ladders only; Kalshi: KXABNB-26NOVNEB Q3 bookings only) | sources/polymarket_search_airbnb_20260917T034148Z.json; sources/kalshi_events_KXABNB_20260917T034148Z.json | 2026-09-17 | 2026-09-17 | no |
| 18 | Web check: the $6bn Aug 2025 and $6bn Feb 2024 programs confirmed; program "does not have an expiration date"; nothing newer | WebSearch query 6 (sources/web_search_log.md); https://finance.yahoo.com/news/airbnb-shares-q2-beat-6-204752718.html | 2025-08-06 | 2026-09-17 | no |
| 19 | Stock sensitivities: one EV/EBITDA turn ≈ $9–10/share; FY27 EPS ≈ $0.0014 per $M of EBITDA; 16 Sep close $167.51; ~590m shares → market cap ≈ $99bn, so $6bn = 6% of market cap | docs/pitch-forecasts/00_BRIEF.md sensitivities | 2026-09-16 | 2026-09-17 | yes |
| 20 | Final 72-hour recency check (query 7): no capital-return news; Chesky's Goldman remarks (8 Sep) did not touch buybacks | WebSearch `Airbnb news this week` | 2026-09-17 | 2026-09-17 | no |

## 2. Query Log
1. [repo] `cat data/processed/abnb_capital_return_quarterly.csv`; pandas dump of buyback and FCF columns of `data/processed/abnb_driver_history_quarterly.csv`
2. [repo] `sed -n '/## 6/,/## 7/p' research/notes/overnight/09_stock-behaviour-and-alpha.md`; `grep -n -i "FCF" docs/margin-build/SYNTHESIS.md`; §3 of SYNTHESIS.md read
3. [repo] regex extraction over `data/raw/letters/*.htm` for "repurchase authorization | authorized ... repurchase | repurchase program" and "remaining/remained ... authorization" and "repurchased ... stock" (python, html stripped)
4. [repo] extraction of debt, cash, funds held, FCF passages from the 1Q26, 2Q26 and 4Q25 letters; `grep -n -i "debt|senior notes" data/raw/letters/1Q26_d23351dex991.htm`
5. [repo] 2Q26 10-Q passages on "repurchase", "remaining", "authoriz" (`data/raw/regulatory/quantification/abnb_2026q2_10q.html`)
6. [repo] `grep -n -i "buyback|repurchase|share count" research/notes/2026-09-13_market-implied-model.md research/notes/2026-09-12_management-implied-model.md`
7. [repo] `grep -n -i "buyback|repurchase" deck/drafts/memo_v2_short_2026-09-16.md`
8. [API] `curl https://gamma-api.polymarket.com/public-search?q=airbnb` (2026-09-17T03:41:48Z); `curl https://api.elections.kalshi.com/trade-api/v2/events?status=open&limit=200&series_ticker=KXABNB`
9. [API] `curl https://efts.sec.gov/LatestSearch/index?q="repurchase program"&ciks=0001559720&forms=8-K` → 403; `curl https://data.sec.gov/submissions/CIK0001559720.json` → 8-K/10-K/10-Q index since 2022
10. [WebFetch] https://news.airbnb.com/ (headlines to 14 Sep 2026)
11. [WebSearch] `Airbnb share repurchase authorization`
12. [model] `python datasets/r06_model.py` (numpy, seed 20260917, N=200,000)
13. [WebSearch, final 72-hour recency] `Airbnb news this week`

## 3. Leading Hypothesis Entities
Airbnb, Brian Chesky, Ellie Mertz, board of directors, share repurchase program, $6 billion authorization, 4Q26 shareholder letter, February 2027 print, 5 November 2026 print

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Off-cycle authorization (8-K between prints, e.g. after a post-5 Nov sell-off) | discarded as a route (kept at ~0 inside the print-day hazard) | 0 of 4 authorizations and 0 off-cycle 8-Ks in the EDGAR index (claims 3, 4); Airbnb's capital-return communication is the letter |
| Announcement at the 5 Nov print | kept, ~0.19 | ~$2.3bn (2.2 quarters of pace) would remain; historically no announcement at readings ≥2.7 and none observed between 1.6 and 2.7, so the rule is interpolated (claim 12) |
| Announcement at the Feb print | kept, main route (~0.57 conditional on no November announcement) | ~1.2–1.3 quarters of pace remaining, inside the 1.0–1.6 band of the two most recent announcements (claim 12); the reverse-DCF note independently expects 4Q26/1Q27 (claim 13) |
| Program allowed to run to exhaustion and renewed at the 1Q27 print (May 2027), outside the window | kept as the main No route (~0.35 of the no-announcement mass) | This is what happened in 2022–23 (claims 2, 12); a slower buyback pace (RNPL cash timing, M&A optionality after the March notes) pushes exhaustion out and the trigger reading up |
| A new program below $5bn (e.g. $3–4bn top-up to preserve M&A capacity) | kept, ~0.22 conditional on an announcement | The last two programs were $6bn (1.3–1.6x FCF); FY26 FCF $4.4–4.8bn supports $5–6bn; but the 2Q26 letter now lists "strategic acquisitions or partnerships" ahead of capital return and the March 2026 notes retained ~$500M (claims 8, 9, 11) |
| 4Q26 repurchases ≥$1.5bn (leg B) on its own | kept, ~0.08 | Needs a +37–43% step-up on the current pace in the seasonally weakest FCF quarter; step-ups of that size happened 2 of 15 times, never opportunistically after a sell-off (claims 6, 7, 10) |
| Accelerated share repurchase announced with a new program | kept inside leg B | No ASR in Airbnb's history; the letter boilerplate lists ASRs as a permitted method only |
| Dividend initiation instead of a bigger buyback | discarded | Not the question's object; no management statement ever raised it |

## 5. Independent Estimates
- base_rate_estimate: 0.50 — Authorization when ≤1.6 quarters of pace remain: 3 of 5 print-states (1Q23, 4Q23, 2Q25 yes; 3Q22, 4Q22 no) = 0.60 by the Feb print (claim 12), × P(size ≥$5bn | announce) = 0.78 (2 of 4 historically, both of the last two; FCF regime supports it, claim 11) = 0.47; plus leg B on the residual 0.53 × 0.07 = 0.04 → 0.51.
- decomposition_estimate: 0.54 — Monte Carlo (`datasets/r06_model.py`): pace N(1.06, 0.13) per quarter → remaining at the Feb print $1.28bn (1.25 quarters); logistic trigger f(r) = 1/(1+e^{2.0(r−1.45)}) fitted to the print-state panel (f(1.0)=0.71, f(1.5)=0.48, f(2.1)=0.21, f(3.3)=0.02) gives P(announce at 5 Nov) 0.19, P(announce Feb | not Nov) 0.57, P(announce by Feb) 0.66; × 0.78 size = leg A 0.51; leg B hazard 0.06 (0.14 after a November authorization) = 0.08; union 0.544.
- anchor_estimate: 0.51 — No market exists (claim 17). Designated anchor: the team's market-implied model input "a new programme is the likely 4Q26 or 1Q27 announcement" (claim 13, 2026-09-13), read as P(announce by Feb) ≈ 0.65 × size 0.78 = 0.51. This is a repo note, not a market, and it shares the buyback panel with this log.
- anchor_value: 0.51
- final_estimate: 0.55
- final_minus_anchor: +0.04 — flag NOT_INDEPENDENTLY_DERIVED applies to the anchor's provenance (a team note, not a market); the base rate (claim 12 count) and the Monte Carlo were built from the letter panel before the note was read and land at 0.50–0.54 on their own.

Reconciliation: the three estimates agree within 5 points. The judgement call above the model is small (+0.01): the model's pace uncertainty (sd 0.13) is if anything generous, and the recent regime (announce with 1–1.6 quarters left, never let it lapse) is the one the 2024–25 board has followed twice.

## 6. Final Numbers
**P(Yes) = 0.55**, credible interval 0.40–0.68.
Decomposition of the Yes mass: authorization ≥$5bn announced at the 5 Nov print ≈ 0.15; at the Feb print ≈ 0.36; 4Q26 repurchases ≥$1.5bn without a qualifying authorization ≈ 0.04. P(4Q26 repurchases ≥$1.5bn) unconditionally ≈ 0.08.
Extreme-probability gate: not triggered.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Pace $1.06bn/q; if $0.90bn/q (RNPL cash timing, M&A reserve) | 0.35 |
| Pace; if $1.20bn/q | 0.67 |
| Trigger rule centred 1.45 quarters; if the board waits until near-exhaustion (centre 1.2, steeper) | 0.43 |
| Trigger rule; if it announces earlier (centre 1.8, 2Q25 style) | 0.65 |
| Trigger rule; if the 2022–23 regime returns (announce only when exhausted) | 0.16 |
| P(size ≥$5bn | announce) 0.78; if 0.60 | 0.44 |
| P(size ≥$5bn | announce); if 0.90 | 0.62 |
| Leg B hazards 0.06/0.14; if doubled | 0.58 |
| Leg B hazards; if zero | 0.51 |
| Joint bear (pace 0.9, exhaustion rule, size 0.6, no leg B) | 0.02 |
| Joint bull (pace 1.2, early rule, size 0.9, leg B doubled) | 0.85 |

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-10-02 | Prelim memo freeze | Quote 0.55 (0.40–0.68); keep the "floor, not catalyst" framing (claim 15) |
| 2026-10-15 to 10-25 | Airbnb IR posts the 3Q26 results date; any 8-K between now and then | An off-cycle 8-K (item 8.01) on a repurchase would resolve leg A immediately (move to ~0.97 pending size); none expected |
| 2026-11-05 | 3Q26 letter: 3Q26 repurchase figure and remaining capacity; any new authorization | New program ≥$5bn → resolve Yes. Remaining ≤$2.0bn with no announcement → 0.62; remaining ≥$2.6bn (3Q26 buyback ≤$0.8bn) → 0.40 |
| 2026-11-06 | Day-1 reaction | A ≥−10% day does not raise leg B on the record (claim 7); no update unless management comments on opportunistic buying |
| 2026-12-15 | Memo scenario refresh | Hazard maintenance only; no decay because the decisive event is the Feb print |
| 2027-02-11 | 4Q26 letter and call | Resolve: new program ≥$5bn or 4Q26 repurchases ≥$1.5bn → Yes; program <$5bn or none, and Q4 <$1.5bn → No |

## 9. Impact
If Yes (weighted by the routes above: ~0.94 of the Yes mass is an authorization at the existing pace, ~0.14 includes a ≥$1.5bn Q4):

| Item | Delta if Yes | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | 0 | capital return does not touch bookings |
| 4Q26 nights (pts) | 0 | as above |
| ADR (pts) | 0 | as above |
| 4Q26 revenue ($M) | 0 | as above |
| FY27 revenue ($M) | 0 | as above |
| FY26 adj. EBITDA margin (pp) | 0 | as above |
| FY27 adj. EBITDA margin (pp) | 0 | as above |
| FY27 EPS ($) | +0.01 (leg A 0.00; leg B +0.03: an extra ~$0.45bn at ~$165 retires ~2.7m shares = 0.47% of 586m diluted × $5.73) | claim 14 (the team path already carries $1.05bn/q, so a new authorization only enables the base path; it does not change it) |
| Stock ($/share) | +1.3 (announcement at the existing pace ≈ +$1.0, i.e. 0.6% on a $99bn market cap, the event-study upper plausible bound given an abnormal return "indistinguishable from zero"; a ≥$1.5bn Q4 ≈ +$2.5 as a pace signal) | claims 3, 19; research/notes/overnight/09_stock-behaviour-and-alpha.md §6 |
| EV = P × stock impact | 0.55 × $1.3 ≈ **+$0.7/share** | |
| Materiality | **Immaterial** (EV < $1/share). The memo can drop the item or keep one clause: a renewal of the $6bn program is the base case, is already in the FY27 share count, and the record shows authorizations are absorbed into the print reaction. What would matter is a step-change in pace (≥$1.5bn a quarter, P ≈ 0.08), which the record has never shown after a sell-off | claim 7, claim 15 |
