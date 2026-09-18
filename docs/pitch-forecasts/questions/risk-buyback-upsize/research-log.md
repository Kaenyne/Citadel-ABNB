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
- revision: 2
- revised: 2026-09-17
- agent: fable
- batch: A11 (with R08 and R09)
- audit: `docs/pitch-forecasts/audits/A11-research-audit.md` (independent Opus auditor standing in for Codex); response `docs/pitch-forecasts/audits/A11-audit-response.md`

## 0b. Question (verbatim)
### Title
Will Airbnb announce a new share repurchase authorization of ≥ $5bn, or repurchase ≥ $1.5bn in a single quarter (4Q26), by the Feb print?
### Resolution Criteria
**Type.** Binary. **Resolution.** Yes on either a board authorization ≥$5bn announced 17 Sep 2026–Feb print, or 4Q26 repurchases ≥$1.5bn per the 4Q26 letter/10-K. Resolution ~11 Feb 2027.
### Fine Print
(none in the registry.) Conventions adopted here and forecast under:
1. The window runs from 17 Sep 2026 through the 4Q26 shareholder letter and call inclusive (an authorization announced in the 4Q26 letter counts; Airbnb has only ever announced authorizations inside the letter, claim 3).
2. "New authorization ≥$5bn" = a board-approved new program or increase whose own size is ≥$5.0bn ("an additional $6 billion" counts on the $6bn; a $3bn top-up does not, whatever the resulting total capacity).
3. "4Q26 repurchases" = the dollar figure the 4Q26 letter gives for the quarter ("During Q4 2026, we repurchased $X of our Class A common stock"); if the letter is silent, the 10-K cash-flow line for the quarter. An accelerated share repurchase counts at notional in the quarter it is executed. (Revision 2, A11-13/14) The letter figure is a trade-basis figure and the letters round quarters of $1bn or more to $0.1bn (2Q26: "$1.1 billion" for a cash-flow line of $1,051M; sub-$1bn quarters are given to the nearest $1M: 807, 838, 857, 749). A letter stating "$1.5 billion" therefore resolves Yes, so the effective bar on the underlying trade-basis figure is $1.45bn; the model tests the simulated quarter at 1.45. The XBRL cash-flow series (`data/processed/abnb_capital_return_quarterly.csv`, `PaymentsForRepurchaseOfCommonStock`) is a different basis and is used only for the pace and FCF history.
4. Either leg resolves Yes; the two legs are correlated (a November authorization raises the chance of a heavier Q4) and are modelled jointly.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Four authorizations to date, all announced in the shareholder letter on a print day: $2.0bn (2 Aug 2022, 2Q22 letter, first program), $2.5bn (9 May 2023, 1Q23 letter, prior program fully used), $6.0bn (13 Feb 2024, 4Q23 letter, $750M of prior remaining), "additional $6 billion" (6 Aug 2025, 2Q25 letter, $1.5bn of prior remaining) | data/raw/letters/2Q22_d353427dex991.htm; 1Q23_d453262dex991.htm; 4Q23_d646462dex991.htm; 2Q25_d17531dex991.htm (regex extraction, query 3); datasets/authorization_history.csv | 2022-08-02 to 2025-08-06 | 2026-09-17 | yes |
| 2 | Remaining capacity at each print (letters): 3Q22 $1.0bn, 4Q22 $0.5bn, 1Q23 $0, 2Q23 $2.0bn, 3Q23 $1.5bn, 4Q23 $0.75bn, 1Q24 $6.0bn, 2Q24 $5.25bn, 3Q24 $4.2bn, 4Q24 $3.3bn, 1Q25 $2.5bn, 2Q25 $1.5bn (+$6bn new), 3Q25 $6.6bn, 4Q25 $5.6bn, 1Q26 $4.5bn, 2Q26 $3.4bn. Every figure re-verified against its letter by the audit (A11 §Scope) and by query 14 | datasets/print_state_panel.csv (from the letters, query 3) | 2022-11-01 to 2026-08-06 | 2026-09-17 | yes |
| 3 | Airbnb has never made an off-cycle capital-return announcement; all four authorizations were inside the letter, on the print, so there is no clean buyback event in the stock. (Revision 2, A11-19: the statement is at lines 21, 186 and 305 of the note, not in its §6 event-study tables; the four day-0 CARs in `data/processed/overnight/09_event_study_events.csv` are Buyback_2.0bn +5.16% (t 1.87), Buyback_2.5bn +2.23% (t 0.87), Buyback_6.0bn +0.22% (t 0.12), Buyback_6.0bn_2 −0.98% (t −0.47), every one confounded with the print) | research/notes/overnight/09_stock-behaviour-and-alpha.md lines 21, 186, 305; data/processed/overnight/09_event_study_events.csv rows 775–778 | 2026-09-07 | 2026-09-17 | yes |
| 4 | EDGAR submissions index: every 8-K with items 2.02/9.01 since 2023 is a print day; off-cycle 8-Ks are 5.07 (AGM), 5.02 (officers), 8.01 (7 Nov, 14 Nov, 13 Dec 2023) and 16 Mar 2026 (1.01/2.03/8.01, the $2.5bn notes). (Revision 2, A11-18) The full-text search returned HTTP 403, so the three 8.01 filings were not opened; the supportable statement is "no off-cycle 8-K of a type that has ever carried a repurchase announcement", and the conclusion that Airbnb announces only in the letter rests on claim 3 | https://data.sec.gov/submissions/CIK0001559720.json ; sources/edgar_submissions_CIK0001559720_20260917T034243Z.json; sources/edgar_fts_8k_repurchase_20260917T034217Z.json (403) | 2026-09-17 | 2026-09-17 | no |
| 5 | Quarterly repurchases, XBRL cash basis (USD m): 3Q22 1,000; 4Q22 500; 1Q23 493; 2Q23 507; 3Q23 500; 4Q23 752; 1Q24 750; 2Q24 749; 3Q24 1,093; 4Q24 838; 1Q25 807; 2Q25 1,010; 3Q25 877; 4Q25 1,095; 1Q26 1,088; 2Q26 1,051. Letter (trade) basis where the two differ: 1Q23 $0.5bn, 2Q23 $500M, 3Q24 "$1.1 billion", 2Q25 "$1.0 billion", 3Q25 **$857M** (cash 877), 4Q25/1Q26/2Q26 "$1.1 billion" (cash 1,095 / 1,088 / 1,051). Maximum single quarter $1,095M cash / "$1.1 billion" letter; last four quarters $0.86–1.10bn on either basis (revision 2, A11-13) | data/processed/abnb_capital_return_quarterly.csv (buybacks_musd; builder analysis/src/capital_return_panel.py:29 uses PaymentsForRepurchaseOfCommonStock); data/raw/letters/*.htm (query 14) | 2026-08-06 | 2026-09-17 | yes |
| 6 | Quarter-on-quarter step-ups of ≥40% in the buyback have happened twice in 15 transitions (3Q23→4Q23 +50%, 2Q24→3Q24 +46%); a "$1.5 billion" Q4 needs +36–43% on the letter-basis $1.1bn / cash-basis $1.05bn pace | computed from claim 5 | 2026-09-17 | 2026-09-17 | yes |
| 7 | No opportunistic step-up after sell-offs: after the −8.0% 7 Aug 2025 print the 3Q25 buyback fell to $857M as reported in the 3Q25 letter ($877M on the cash-flow line) from $1.0bn ($1,010M cash); after the −6.15% 3 Feb 2026 AI scare the 1Q26 buyback was "$1.1 billion" ($1,088M cash) vs "$1.1 billion" ($1,095M) (revision 2, A11-13) | claim 5; research/notes/overnight/09_stock-behaviour-and-alpha.md named events | 2026-09-07 | 2026-09-17 | yes |
| 8 | 2Q26 letter: "During Q2 2026, we repurchased $1.1 billion ... As of June 30, 2026, we had the authorization to purchase up to $3.4 billion". The capital-allocation sentence "prioritizes investments in organic growth, strategic acquisitions or partnerships, and return of capital to shareholders, in that order" is boilerplate carried since 2Q22; its only wording change ("where relevant" → "or partnerships") first appears in the 2Q25 letter, the same letter that announced the additional $6bn (revision 2, A11-04: regex over all 23 letters; 1Q24, 1Q25, 2Q22, 2Q24, 3Q24, 4Q23, 4Q24 = "where relevant"; 2Q25, 3Q25, 4Q25, 1Q26, 2Q26 = "or partnerships"). It is not evidence for a smaller program | data/raw/letters/2Q26_d70413dex991.htm; all letters (query 15) | 2026-08-06 | 2026-09-17 | yes |
| 9 | Balance sheet 30 Jun 2026: $12.1bn cash, equivalents, short-term investments and restricted cash; $12.2bn funds held; long-term debt $2,476M; $2.5bn senior notes issued March 2026 (of which $2.0bn repaid the 2026 converts, ~$500M retained) | data/raw/letters/2Q26_d70413dex991.htm; data/raw/regulatory/quantification/abnb_2026q2_10q.html | 2026-08-06 | 2026-09-17 | no |
| 10 | FY26 FCF $4.4–4.8bn (bias-adjusted $4,445M, mid $4,844M); FY27 $4.9–5.3bn; quarterly FCF not forecast (M7 failed); 4Q FCF is the seasonal low (4Q25 $521M, 4Q24 $458M) | docs/margin-build/SYNTHESIS.md §3; data/processed/abnb_capital_return_quarterly.csv | 2026-09-15 | 2026-09-17 | yes |
| 11 | Program size vs trailing FY FCF: $2.0bn/3.4 = 0.59x (2022), $2.5bn/3.4 = 0.74x (2023), $6.0bn/3.8 = 1.58x (2024), $6.0bn/4.5 = 1.33x (2025). On FY26 FCF $4.4–4.8bn the recent-regime multiples imply $5.9–7.6bn; the early-regime multiples imply $2.6–3.6bn; a $5bn program is 1.05–1.14x, $6bn 1.25–1.36x | datasets/authorization_history.csv (FCF from claim 5's source, fcf_musd_ltm) | 2026-09-17 | 2026-09-17 | yes |
| 12 | Trigger arithmetic: at the 5 Nov print remaining ≈ $3.4bn − 3Q26 pace (≈$2.3bn, ~2.2 quarters of pace); at the Feb print ≈ $1.2–1.3bn (~1.1–1.3 quarters). The three defined announcement readings are points, n = 3: r = 0.0 (1Q23), 1.2 (4Q23), 1.6 (2Q25); the 2Q22 first program has no prior. Non-announcements at 1.0 and 0.7 (3Q22, 4Q22, the run-to-exhaustion episode) and at every reading ≥2.7 (0 of 11). No print has ever fallen in 1.6 < r < 2.7 (revision 2, A11-15, A11-05) | datasets/print_state_panel.csv; datasets/r06_model_v2.py | 2026-09-17 | 2026-09-17 | yes |
| 13 | Team's market-implied model holds buybacks at $1,050M a quarter, "which exhausts the $3.4bn authorisation by 2Q27, so a new programme is the likely 4Q26 or 1Q27 announcement" | research/notes/2026-09-13_market-implied-model.md (inputs paragraph) | 2026-09-13 | 2026-09-17 | no |
| 14 | Team FY27 path already assumes continued buybacks: diluted shares 595.8m FY26 → 573.0m FY27 (line build), 570.7m end-FY27 (reverse DCF, after $6.3bn of buybacks) | docs/margin-build/SYNTHESIS.md §3 annual table; research/notes/2026-09-13_market-implied-model.md | 2026-09-15 | 2026-09-17 | yes |
| 15 | Memo risk 6 already frames the buyback as "a floor on sell-offs, not a catalyst" | deck/drafts/memo_v2_short_2026-09-16.md, Risks item 6 | 2026-09-16 | 2026-09-17 | no |
| 16 | Newsroom snapshot saved 2026-09-17T13:22Z (revision 2, A11-24): latest items "Airbnb launches new housing accelerator" (14 Sep), "Airbnb announces Pepijn Rijvers as Chief Business Officer" (1 Sep), Q2 2026 financial results (6 Aug); no capital-return item and no Q3 results date in the snapshot | sources/newsroom_news.airbnb.com_20260917T132231Z.html | 2026-09-14 | 2026-09-17 | no |
| 17 | No Polymarket or Kalshi market on Airbnb capital return (Polymarket: closed 2Q26 GBV ladders and price-hit ladders only; Kalshi: KXABNB-26NOVNEB Q3 bookings only) | sources/polymarket_search_airbnb_20260917T034148Z.json; sources/kalshi_events_KXABNB_20260917T034148Z.json | 2026-09-17 | 2026-09-17 | no |
| 18 | Web check: the $6bn Aug 2025 and $6bn Feb 2024 programs confirmed; program "does not have an expiration date"; nothing newer | WebSearch query 6 (sources/web_search_log.md); https://finance.yahoo.com/news/airbnb-shares-q2-beat-6-204752718.html | 2025-08-06 | 2026-09-17 | no |
| 19 | Stock sensitivities: one EV/EBITDA turn ≈ $9–10/share; FY27 EPS ≈ $0.0014 per $M of EBITDA; 16 Sep close $167.51; ~590m shares → market cap ≈ $99bn, so $6bn = 6% of market cap | docs/pitch-forecasts/00_BRIEF.md sensitivities | 2026-09-16 | 2026-09-17 | yes |
| 20 | Final 72-hour recency check (query 7): no relevant result in the searches recorded on capital return; Chesky's Goldman remarks (8 Sep) did not touch buybacks (revision 2, A11-24 wording) | WebSearch `Airbnb news this week` (sources/web_search_log.md) | 2026-09-17 | 2026-09-17 | no |
| 21 | (Revision 2, A11-03) Maximum-likelihood logistic of announcement on quarters-of-pace remaining over the 16-print panel: logit = 1.5308 − 1.4234·r, i.e. k = 1.423, r50 = 1.075, negative log-likelihood 4.111; the revision-1 hand-set rule (k 2.0, r50 1.45) scores 4.492. Fitted values at r = 1.0 / 1.2 / 1.25 / 1.6 / 2.2: MLE 0.527 / 0.456 / 0.438 / 0.322 / 0.168; hand-set 0.711 / 0.623 / 0.599 / 0.426 / 0.182. The fit has 3 events on 16 rows, three of which (3Q22, 4Q22, 1Q23) are one board episode; collapsing that episode to its terminal row leaves the fit unidentified (perfect separation), so neither rule is "fitted" in a usable sense and revision 2 blends them | docs/pitch-forecasts/audits/A11-reproduce.py output (audits/A11-reproduce.stdout.txt); datasets/r06_model_v2.py | 2026-09-17 | 2026-09-17 | yes |
| 22 | (Revision 2, A11-16) The "3 of 5 print-states at r ≤ 1.6" are three board episodes, not five decisions: (i) 2022–23, the first $2bn allowed to run to exhaustion (no at 1.0, no at 0.7, renewed at 0.0 with $2.5bn); (ii) Feb 2024, renewed at 1.2 ($750M left) with $6bn; (iii) Aug 2025, renewed at 1.6 ($1.5bn left) with $6bn. Two of three renewed before exhaustion; Laplace (2+1)/(3+2) = 0.60 for "renewed by the ~1.25-quarter reading" | datasets/print_state_panel.csv; 3Q22, 4Q22, 1Q23 letters | 2026-09-17 | 2026-09-17 | yes |
| 23 | (Revision 2, A11-05) Third-quarter prints: 0 of 4 carried an authorization (3Q22 r 1.0 in the exhaustion regime; 3Q23 r 3.0, 3Q24 r 4.9, 3Q25 r 7.1 — all outside any trigger band). The count is uninformative about a November seasonality because no 3Q print has ever occurred inside the band where the board has renewed | datasets/print_state_panel.csv | 2026-09-17 | 2026-09-17 | yes |
| 24 | (Revision 2) Dollar-remaining readings: the board renewed with $0 / $0.75bn / $1.5bn remaining and did not renew with $2.5bn (1Q25), $3.3bn, $4.2bn remaining. The expected ~$2.3bn at the 5 Nov print sits inside the observed band on dollars (between $1.5bn yes and $2.5bn no) even though it sits in the unobserved gap on quarters of pace; a uniform dollar threshold on ($1.5bn, $2.5bn) gives P(threshold > $2.3bn) = 0.20, times P(recent regime) 2/3 = 0.13; the same construction on quarters of pace (threshold uniform on (1.6, 2.7), P(> 2.2) = 0.45) gives 0.30 | datasets/print_state_panel.csv; computed | 2026-09-17 | 2026-09-17 | yes |
| 25 | (Revision 2) Sibling comparisons, not anchors: the audit's independent construction (Nov 0.08, MLE Feb rule, size 0.78) gives 0.42 (reproduced at 0.421 in `r06_model_v2.py`); the team note (claim 13) read as P(announce by Feb) ≈ 0.65 × size 0.50–0.75 = 0.33–0.49 | docs/pitch-forecasts/audits/A11-research-audit.md; datasets/r06_v2_sensitivity.csv | 2026-09-17 | 2026-09-17 | no |

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
14. [repo, revision 2] `py -3.13 -B docs/pitch-forecasts/audits/A11-reproduce.py` (letter-stated repurchase figure vs XBRL cash line for every quarter; remaining-authorization regex; MLE grid search; stdlib Monte Carlo replay)
15. [repo, revision 2] regex over all 23 letters for "During Q\d \d{4}, we repurchased", "authorization to purchase up to", and "prioritizes investments in organic growth, (…), and return of capital" (boilerplate wording by letter)
16. [repo, revision 2] EDGAR submissions JSON: 10-K and item-2.02 8-K filing dates 2024–2026 (10-K 2026-02-12, 2025-02-13, 2024-02-16; February prints 2026-02-12, 2025-02-13, 2024-02-13)
17. [repo, revision 2] `grep -n -i buyback data/processed/overnight/09_event_study_events.csv`; lines 180–195 and 300–310 of research/notes/overnight/09_stock-behaviour-and-alpha.md
18. [web, revision 2] `curl -sL https://news.airbnb.com/` saved to sources/newsroom_news.airbnb.com_20260917T132231Z.html; headline and date extraction
19. [model, revision 2] `py -3.13 datasets/r06_model_v2.py` (numpy, seed 20260917, N=200,000; outputs r06_v2_summary.csv, r06_v2_sensitivity.csv)

## 3. Leading Hypothesis Entities
Airbnb, Brian Chesky, Ellie Mertz, board of directors, share repurchase program, $6 billion authorization, 4Q26 shareholder letter, February 2027 print, 5 November 2026 print

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Off-cycle authorization (8-K between prints, e.g. after a post-5 Nov sell-off) | discarded as a route (kept at ~0 inside the print-day hazard) | 0 of 4 authorizations off-cycle (claim 3); no off-cycle 8-K of a type that has ever carried one (claim 4); Airbnb's capital-return communication is the letter |
| Announcement at the 5 Nov print | kept, 0.12 (revision 2; was 0.19) | ~$2.3bn (2.2 quarters of pace) would remain: inside the observed band on dollars (claim 24), inside the never-observed 1.6–2.7 gap on quarters of pace (claim 12). The logistic interpolations give 0.17–0.18, the dollar-threshold reading 0.13, the pace-threshold reading 0.30, the auditor's cap 0.08 (borrowed from the r ≥ 2.7 cell, which is not the relevant cell). 0.12 is a judgement below the interpolation because the board has never renewed with more than $1.5bn left and the 3Q letter has never carried a program; the 0-of-4 third-quarter count itself is uninformative (claim 23) |
| Announcement at the Feb print | kept, main route (~0.52 conditional on no November announcement; revision 2, was 0.57) | ~1.25 quarters (~$1.28bn) remaining, at or below the readings of the two most recent renewals (1.2 and 1.6; claim 12); two of three episodes renewed before exhaustion (claim 22); the MLE rule gives 0.44 at 1.25 and the hand-set rule 0.60, and neither is identified on n = 16 with 3 events (claim 21), so the model blends them |
| Program allowed to run to exhaustion and renewed at the 1Q27 print (May 2027), outside the window | kept as the main No route (~0.4 of the no-announcement mass) | This is what happened in 2022–23 (claims 2, 22); a slower buyback pace (RNPL cash timing, M&A optionality after the March notes) pushes exhaustion out and the trigger reading up |
| A new program below $5bn (e.g. $3–4bn top-up to preserve M&A capacity) | kept, 0.25 conditional on an announcement (revision 2; was 0.22) | Historical frequency of ≥$5bn is 2 of 4 = 0.50 (A11-02); the recent regime (2 of 2 programs since the company reached scale at 1.33–1.58x FCF, the "additional $6 billion" precedent, FY26 FCF $4.4–4.8bn supporting $5.9–7.6bn on those multiples) is weighted 0.75, a reversion to the early-regime sizing (0.59–0.74x FCF → $2.6–3.6bn) 0.25. The capital-allocation boilerplate is no longer cited (claim 8); the March 2026 notes' retained ~$500M and RNPL cash timing remain the arguments for a smaller top-up |
| 4Q26 repurchases ≥$1.5bn (leg B) on its own | kept, ~0.07 unconditional | Needs a +36–43% step-up on the current pace in the seasonally weakest FCF quarter; step-ups of that size happened 2 of 15 times, never opportunistically after a sell-off (claims 6, 7, 10); the letter's rounding puts the effective bar at $1.45bn (convention 3) |
| Accelerated share repurchase announced with a new program | kept inside leg B | No ASR in Airbnb's history; the letter boilerplate lists ASRs as a permitted method only |
| Dividend initiation instead of a bigger buyback | discarded | Not the question's object; no management statement ever raised it |

## 5. Independent Estimates
- base_rate_estimate: 0.35 — Pure frequencies, no size judgement (revision 2, A11-02): P(renewed by the ~1.25-quarter reading) from the three board episodes, Laplace (2+1)/(3+2) = 0.60 (claim 22; the five-print-state count 3/5 gives the same 0.60), × P(size ≥$5bn | announce) at the historical frequency 2 of 4 = 0.50 (claim 1) = 0.30; plus leg B on the residual 0.70 × 0.07 = 0.05 → 0.35. Regime conditioning (the last two programs' size multiple, claim 11) is deliberately left to the decomposition so that this estimate does not share its judgement.
- decomposition_estimate: 0.47 — Monte Carlo (`datasets/r06_model_v2.py`): pace N(1.06, 0.13) per quarter → remaining at the Feb print $1.28bn (1.25 quarters); November hazard 0.12 (judgement, claim 24); February trigger = 50/50 blend of the MLE logistic (k 1.423, r50 1.075) and the hand-set rule (k 2.0, r50 1.45) evaluated at the simulated reading (claim 21) → P(announce Feb | not Nov) 0.52, P(announce by Feb) 0.58; × P(size ≥$5bn | announce) 0.75 (regime judgement, labelled; claim 11) = leg A 0.43; leg B hazard 0.06 (0.14 after a November authorization) tested at $1.45bn = 0.07; union 0.469.
- anchor_estimate: none — No market exists (claim 17). The revision-1 "anchor" (the team note, claim 13, read as 0.65 × 0.78) was built from the same size judgement as the other two estimates (A11-02) and is a repo note, not a market; it is withdrawn as an anchor and kept as a labelled sibling comparison (claim 25: 0.33–0.49 depending on the size frequency used), alongside the audit's independent 0.42. The three-estimate requirement of the skill is therefore unmet: two internal estimates and no external anchor.
- anchor_value: n/a (NO_EXTERNAL_ANCHOR)
- final_estimate: 0.46
- final_minus_anchor: n/a. Against the sibling comparisons: +0.04 vs the audit's 0.42 (the difference is the November hazard 0.12 vs 0.08 and the blended Feb rule vs the MLE alone, partly offset by size 0.75 vs 0.78); −0.09 vs revision 1.

Reconciliation: the base rate (0.35) and the decomposition (0.47) differ by 12 points, and the whole gap is the size judgement (0.50 frequency vs 0.75 regime) plus the regime-conditioned Feb hazard (0.52 vs the episode Laplace 0.60 × the MLE shading). The three estimates in revision 1 "agreed within 5 points" only because all three multiplied by the same 0.78; revision 2 reports the disagreement instead of averaging it away. Final 0.46: the decomposition shaded one point toward the frequency base rate, because the size judgement rests on two observations.

## 6. Final Numbers
**P(Yes) = 0.46**, credible interval 0.30–0.60 (widened from 0.40–0.68 per A11-16: three independent episodes, not five decisions; a size judgement resting on two programs).
Decomposition of the Yes mass (model, scaled): authorization ≥$5bn announced at the 5 Nov print ≈ 0.09; at the Feb print ≈ 0.33; 4Q26 repurchases ≥$1.5bn without a qualifying authorization ≈ 0.04. P(4Q26 repurchases ≥$1.5bn) unconditionally ≈ 0.07; P(any new authorization by Feb) ≈ 0.58.
Extreme-probability gate: not triggered.
Coherence: independent of R08 and R09 (no shared switch).

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| November hazard 0.12; if 0.08 (auditor's cap) | 0.46 (model 0.456) |
| November hazard; if 0.20 (logistic interpolation) / 0.30 (pace-threshold model) | 0.50 / 0.53 |
| Feb rule blend; if the MLE logistic alone (0.44 at 1.25 quarters) | 0.42 |
| Feb rule; if the revision-1 hand-set rule alone (0.60 at 1.25) | 0.52 |
| Feb rule; if the 2022–23 exhaustion regime returns (announce only when exhausted) | 0.23 |
| Pace $1.06bn/q; if $0.90bn/q (RNPL cash timing, M&A reserve) | 0.34 |
| Pace; if $1.20bn/q | 0.57 |
| P(size ≥$5bn \| announce) 0.75; if 0.50 (historical frequency) | 0.34 |
| P(size ≥$5bn \| announce); if 0.90 | 0.55 |
| Leg B hazards 0.06/0.14; if doubled | 0.51 |
| Leg B hazards; if zero | 0.43 |
| Leg B threshold 1.50 (no rounding convention) | 0.47 (unchanged to rounding) |
| Auditor's construction (Nov 0.08, MLE Feb, size 0.78) | 0.42 |
| Revision-1 construction (Nov 0.19, hand-set rule, size 0.78, threshold 1.5) | 0.55 |
| Joint bear (pace 0.9, exhaustion rule, Nov 0.05, size 0.5, no leg B) | 0.04 |
| Joint bull (pace 1.2, hand-set rule, Nov 0.25, size 0.9, leg B doubled) | 0.77 |

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-10-02 | Prelim memo freeze | Quote 0.46 (0.30–0.60); keep the "floor, not catalyst" framing (claim 15) |
| 2026-10-15 to 10-25 | Airbnb IR posts the 3Q26 results date; any 8-K between now and then | An off-cycle 8-K (item 8.01) on a repurchase would resolve leg A immediately (move to ~0.97 pending size); none expected (claims 3, 4) |
| 2026-11-05 | 3Q26 letter: 3Q26 repurchase figure and remaining capacity; any new authorization | New program ≥$5bn → resolve Yes; program <$5bn → 0.08 (leg B only, raised for the pace signal). No program: remaining ≈ $2.3bn → 0.43; remaining ≤$2.0bn (3Q26 buyback ≥$1.4bn) → 0.55; remaining ≥$2.6bn (3Q26 buyback ≤$0.8bn) → 0.22 (model re-run at the stated reading; `r06_model_v2.py` with `remaining` set to the letter figure) |
| 2026-11-06 | Day-1 reaction | A ≥−10% day does not raise leg B on the record (claim 7); no update unless management comments on opportunistic buying |
| 2026-12-15 | Memo scenario refresh | Hazard maintenance only; no decay because the decisive event is the Feb print |
| 2027-02-11 | 4Q26 letter and call | Resolve: new program ≥$5bn or the letter's 4Q26 repurchase figure "$1.5 billion" or more → Yes; program <$5bn or none, and Q4 below "$1.5 billion" → No |
| 2027-02-11 to 02-16 | FY2026 10-K | Only relevant if the letter omits the quarterly figure (convention 3); two of the last three 10-Ks filed on the print day |

## 9. Impact
If Yes (weighted by the routes above: ~0.85 of the Yes mass is an authorization at the existing pace, ~0.15 includes a ≥$1.5bn Q4; P(leg B | Yes) = 0.071/0.469 = 0.152 in the model):

| Item | Delta if Yes | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | 0 | capital return does not touch bookings |
| 4Q26 nights (pts) | 0 | as above |
| ADR (pts) | 0 | as above |
| 4Q26 revenue ($M) | 0 | as above |
| FY27 revenue ($M) | 0 | as above |
| FY26 adj. EBITDA margin (pp) | 0 | as above |
| FY27 adj. EBITDA margin (pp) | 0 | as above |
| FY27 EPS ($) | 0.00 (leg A 0.00; leg B +$0.027: an extra ~$0.45bn at ~$165 retires 2.73m shares = 0.47% of 586m diluted × $5.73 = $0.027; weighted 0.152 × 0.027 = $0.004) (revision 2, A11-17) | claim 14 (the team path already carries $1.05bn/q, so a new authorization only enables the base path; it does not change it) |
| Stock ($/share) | +1.2 (announcement at the existing pace ≈ +$1.0, i.e. 0.6% on a $99bn market cap, an upper plausible bound consistent with the four confounded day-0 CARs in claim 3; a ≥$1.5bn Q4 ≈ +$2.5 as a pace signal; weighted 0.848 × 1.0 + 0.152 × 2.5 = $1.23) (revision 2, A11-17) | claims 3, 19 |
| EV = P × stock impact | 0.46 × $1.2 ≈ **+$0.6/share** | |
| Materiality | **Immaterial** (EV < $1/share). The memo can drop the item or keep one clause: a renewal of the $6bn program is the modal outcome, is already in the FY27 share count, and the record shows authorizations are absorbed into the print reaction. What would matter is a step-change in pace (≥$1.5bn a quarter, P ≈ 0.07), which the record has never shown after a sell-off | claim 7, claim 15 |

## 10. Revision notes
| Change | Finding |
|---|---|
| Metadata: revision 2, revised 2026-09-17; audit and response paths added | — |
| Convention 3: letter (trade) basis stated; $0.1bn rounding above $1bn written in; effective leg-B bar $1.45bn; model tests 1.45 | A11-13, A11-14 |
| Claim 5 and claim 7: both bases quoted; 3Q25 "$857M as reported in the 3Q25 letter ($877M on the cash-flow line)" | A11-13 |
| Claim 8: capital-allocation boilerplate identified as unchanged since 2Q22 (wording change first in 2Q25, the $6bn letter); removed as evidence for a smaller program | A11-04 |
| Claim 12 and claim 22: announcement readings quoted as three points (0.0, 1.2, 1.6), n = 3; three board episodes, not five decisions; interval widened to 0.30–0.60 | A11-15, A11-16 |
| Claim 21: MLE logistic reported (k 1.423, r50 1.075, nll 4.111 vs 4.492); "fitted" withdrawn; February rule = 50/50 blend of MLE and hand-set rule; the fit's non-identification on episodes recorded | A11-03 |
| November hazard: logistic extrapolation replaced by a fixed judgement 0.12 with the unobserved-region argument priced; the auditor's 0.08 cap, the dollar-threshold 0.13 and pace-threshold 0.30 readings reported as sensitivities; the 0-of-4 third-quarter count shown to be uninformative (claim 23, claim 24) | A11-05 (accepted in part) |
| P(size ≥$5bn \| announce): 0.78 → 0.75, labelled a regime judgement; historical frequency 0.50 published; base-rate estimate rebuilt without it (0.35) | A11-02 |
| Anchor withdrawn (NO_EXTERNAL_ANCHOR); team note and audit number kept as labelled sibling comparisons (claim 25); three-estimate requirement stated unmet | A11-02, A11-08 (applied consistently) |
| Claim 3: event-study citation corrected to lines 21/186/305 and the four day-0 CARs from `09_event_study_events.csv` | A11-19 |
| Claim 4: "no off-cycle 8-K of a type that has ever carried one"; 403 on the full-text search recorded | A11-18 |
| Claims 16 and 20: newsroom snapshot saved (`sources/newsroom_news.airbnb.com_20260917T132231Z.html`); "no relevant result in the searches recorded" wording | A11-24 |
| §9: FY27 EPS 0.00 (was +0.01); stock +$1.2 (was +$1.3); EV +$0.6 (was +$0.7); P(leg B \| Yes) 0.152 from the model | A11-17 |
| §6: P(Yes) 0.55 → 0.46; route split re-stated; §7 rebuilt from `r06_v2_sensitivity.csv`; §8 November branches recomputed | A11-02, A11-03, A11-05 |
| Queries 14–19 appended; `datasets/r06_model_v2.py`, `r06_v2_summary.csv`, `r06_v2_sensitivity.csv` added (revision-1 files untouched) | — |
