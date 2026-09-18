# RESEARCH LOG

Revision 2 (2026-09-17, audit response to `audits/A12-research-audit.md`, Fable 5.1; revision 1 of 2026-09-17 was the initial forecast, batch A12 with R10, R15, R16). Reproduction, in order: [datasets/r11_extract_lodging_monthly.py](datasets/r11_extract_lodging_monthly.py) (`py -3.13`, stdlib only; parses the 58 saved Lodging Magazine snapshots in [sources/lodging_monthly/](sources/lodging_monthly/) into `us_revpar_monthly_yoy_measured.csv` and `r11_extract_report.txt`) then [datasets/r11_model_v2.py](datasets/r11_model_v2.py) (`py -3.13`, numpy/scipy, deterministic, <2 s; writes `r11_v2_quarterly_base_rate.csv`, `r11_v2_path.csv`, `r11_v2_views.csv`, `r11_v2_sensitivity.csv` and **`r11_v2_joint_object.json`** — the one 4Q26 US RevPAR object R11, B15 and X01 must read). Revision-1 `r11_model.py` and its CSVs are left in place as the audit trail. Weekly STR series copied from the repo: [datasets/str_weekly_us_3q26_repo_copy.csv](datasets/str_weekly_us_3q26_repo_copy.csv).

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
- revision: 2
- revised: 2026-09-17
- agent: fable

## 0b. Question (verbatim)
### Title
Will STR's US hotel RevPAR growth for 4Q26 (Oct–Dec, as reported by STR/CoStar in Jan 2027) be ≥ +4% y/y?
### Resolution Criteria
**Type.** Binary. **Resolution.** Yes if the quarterly (or the average of the three monthly) US RevPAR y/y ≥ 4.0%. Resolution ~25 Jan 2027.
### Fine Print
(none in the registry.) Conventions adopted: (1) the resolving series is CoStar/STR's US monthly "hotel performance" release (occupancy × ADR = RevPAR, all-US, y/y on the same-month basis STR reports); the October release lands ~20 Nov, November ~20 Dec, December ~22 Jan 2027, so the average of the three monthly y/y figures is the practical resolver (a simple mean; STR's own Q4 figure, if it publishes one in the full-year release, governs where both exist); (2) trade-press reprints (Lodging, Hotel Dive, Hospitality Net) of the STR release count as the source when costar.com is unreachable — **this convention now also governs the historical base rate: the 28 months in `us_revpar_monthly_yoy_measured.csv` are Lodging Magazine reprints of the CoStar monthly release, parsed from saved HTML** (A12-03); (3) if STR revises a month, the values as published at the January read govern; (4) 4.0% exactly resolves Yes.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | CoStar/STR US weekly 3Q26: July month occ 69.7% (+2.3%), ADR $171.74 (+5.7%), RevPAR $119.77 (+8.2%; NYC ADR +24% on the World Cup final); weeks ending 1 Aug RevPAR +7.3%, 8 Aug +7.2% (18th straight weekly gain; 79 days of summer +7.4%, strongest since 2022), 15 Aug +6.2% (ADR +3.5%), 22 Aug +4.4% (ADR +2.3%), 29 Aug +1.7% (ADR +0.6%; slowest since April; Labor Day one week later), 5 Sep +16.1% (calendar mirror image, not a demand signal) | `data/processed/q3nowcast/G/str_weekly_us_3q26.csv` (Lodging Magazine / CoStar reprints, URLs inside); `research/notes/q3nowcast/G_external-sources-q3-read.md` §1 item 1 | 2026-08-06 to 2026-09-11 | 2026-09-17 | yes |
| 2 | CoStar/Tourism Economics forecast, 7–10 Aug 2026: FY2026 RevPAR +4.4% (raised from +2.8% on 2 Jun), demand +1.7%, ADR +3.1%, occupancy 63.1%; H1 2026 sold 11.4m incremental room-nights "fueled in part by the World Cup and America 250"; FY2027 RevPAR +2.1%, ADR +1.6%, demand +1.1%; supply +0.4% (2026) / +0.6% (2027); June 2027 RevPAR −0.8% on the World Cup comparison; luxury double-digit RevPAR in Q2 and Q3 2026; **no quarterly or H2 path published**. Primary citation is now the repo note, which is dated and in-repo; the trade-press pages are saved as secondary (A12-11) | `research/notes/overnight/05_macro-outlook-and-transmission.md` §4.5 (primary); [sources/hotelnewsresource_costar_forecast_10aug2026_20260917T134945Z.html](sources/hotelnewsresource_costar_forecast_10aug2026_20260917T134945Z.html), [sources/hoteldive_costar_te_raise_outlook_aug2026_20260917T140129Z.html](sources/hoteldive_costar_te_raise_outlook_aug2026_20260917T140129Z.html) | 2026-08-10 (repo note 2026-09-06) | 2026-09-17 | yes |
| 3 | CoStar/TE June forecast (2 Jun 2026): FY26 RevPAR +2.8%, ADR +2.0%, occupancy 62.8%; "January–April RevPAR +4% year over year"; Q1 2026 RevPAR the highest on record; World Cup bookings "tracked below expectations"; TE's World Cup lift +1.7% RevPAR in June–July, +0.4% full-year | [sources/hoteldive_costar_te_forecast_jun2026_20260917T140129Z.html](sources/hoteldive_costar_te_forecast_jun2026_20260917T140129Z.html) (https://www.hoteldive.com/news/costar-tourism-economics-hotel-revpar-forecast-2026/821683/) | 2026-06-02 | 2026-09-17 | yes |
| 4 | **Measured US monthly RevPAR y/y, 28 months Jul 2023 – Jul 2026**, each parsed from a saved Lodging Magazine reprint of the CoStar monthly release with its own publication date: 2023 Jul +0.8, Aug +1.5, Nov +2.4; 2024 Jan +0.9, Apr +2.0, May +4.0, Jun +1.5, Jul 0.0, Aug +3.9, Sep −1.3, Dec +4.4; 2025 Jan +4.5, Feb +1.9, Mar +0.8, Apr −0.1, May +0.1, Jun −1.2, Jul −1.1, Aug −1.0, Sep −2.1, **Oct −0.9**, Nov −2.3; 2026 Jan +0.4, Feb +4.3, Apr +4.4, May +4.0, Jun +8.4, Jul +8.2. Of 58 saved pages, 30 are weekly or P&L (GOPPAR/TRevPAR) releases and are rejected by the parser with the reason recorded in `r11_extract_report.txt` | [datasets/us_revpar_monthly_yoy_measured.csv](datasets/us_revpar_monthly_yoy_measured.csv), [datasets/r11_extract_report.txt](datasets/r11_extract_report.txt), [sources/lodging_monthly/](sources/lodging_monthly/) | 2023-08-22 to 2026-08-26 | 2026-09-17 | yes |
| 5 | Two figures in the quarterly reconstruction are **not** from a saved snapshot and are flagged in every output: March 2026 +5.9% (repo note; the CoStar March release is not among the saved pages) and December 2025 −2.2% (implied by FY2025 RevPAR −0.3%, the annual release, net of the three measured 2025 quarters at equal weights). FY2025: occupancy 62.3% (−1.2%), ADR $160.54 (+0.9%), RevPAR $100.02 (−0.3%), the first annual decline since 2020 | `research/notes/overnight/06_consumer-choice-and-willingness-to-pay.md` §1.2; [sources/hoteldive_fy2025_us_hotel_performance_20260917T135000Z.html](sources/hoteldive_fy2025_us_hotel_performance_20260917T135000Z.html); computed in `r11_model_v2.py` | 2026-01-22 / 2026-09-06 | 2026-09-17 | yes |
| 6 | **Quarterly base rate, from claim 4 (the measured months) rather than from a hand list:** 2023Q3 +1.15 (n 2), 2024Q2 +2.50, 2024Q3 +0.87, 2025Q1 +2.40, 2025Q2 −0.40, 2025Q3 −1.40, 2025Q4 −1.80 (Dec implied), 2026Q1 +3.53 (Mar from the note), 2026Q2 +5.60. **≥ +4.0% in 1 of 9 quarters (Laplace 0.18); ≤ +1.0% in 4 of 9 (Laplace 0.45).** On the six quarters with all three months snapshotted: 1 of 6 and 3 of 6 (Laplace 0.25 / 0.50). Revision 1's "1 of 13 quarters ≥ +4%" and B15's "6 of 13 ≤ +1%" were the hand-entered list at `r11_model.py:36` and are **withdrawn** | [datasets/r11_v2_quarterly_base_rate.csv](datasets/r11_v2_quarterly_base_rate.csv) | 2026-09-17 | 2026-09-17 | yes |
| 7 | 2026 monthly hotel pricing colour: STR ADR Mar +3.8%, Jul +5.7%; CPI lodging away from home Jan −1.9, Feb −1.1, Mar +2.5, Apr +4.4, May +5.0, Jun +4.7, Jul +2.8; July 2026 luxury RevPAR +17.7% vs economy +3.6% (barbelled) | `research/notes/overnight/06_consumer-choice-and-willingness-to-pay.md` §1.2 | 2026-09-06 | 2026-09-17 | yes |
| 8 | 4Q25 calendar record: the week of 2–8 Nov 2025 printed +6.2% "from a straightforward comparison" with the 2024 election week (STR's Collazo); the 39-day shutdown cost ~1.5m room-nights, "minimal disruption"; two weeks to 29 Nov −0.3%; "US hotel performance declines continue throughout December" | https://hoteldata.com/blogs/str-november-2025-hotel-performance/ (search snippet, unsaved: str.com and costar.com return 403 to fetchers); `research/notes/overnight/06_consumer-choice-and-willingness-to-pay.md` §1.2 | 2025-11 to 2026-01 | 2026-09-17 | yes |
| 9 | Operators at Q2: Marriott FY26 RevPAR raised to 3.0–3.5% (US & Canada +5.0% in Q2; World Cup ~45bp of FY global RevPAR; July +7% global, +8% US & Canada, +5% ex-World Cup, group "turned upwards"); Hilton raised to 3.0–3.5%; Hyatt 3.5–4.5% maintained, Q3 system-wide ~+3%; Wyndham 0–1%, Choice US 0–1.25%. An H1 near +4% inside a 3.0–3.5% FY implies operator H2 near +2.5%. These are **system-wide global** figures, a different object from all-US STR (the repo's only quarterly hotel series, `q3nowcast/G/G_quarterly_panel.csv`, is likewise operator/global) | `research/notes/overnight/05_macro-outlook-and-transmission.md` §4.5, §4.8; `data/processed/q3nowcast/G/intra_quarter_commentary.csv` rows 55, 58, 63; `data/processed/q3nowcast/G/G_quarterly_panel.csv` | 2026-07-28 to 2026-09-09 | 2026-09-17 | yes |
| 10 | Macro backdrop: unemployment 4.1%, payrolls +162k (Aug), claims −10% y/y, sentiment recession-adjacent (Michigan 55.2), Fed hiked 16 Sep to 3.75–4.00% with three more priced; TSA throughput −3.7% y/y (Aug) as fares ration air travel; CR expires 11 Dec 2026; midterms 3 Nov 2026 | `05_macro-outlook-and-transmission.md` §4.1, §4.4, §4.9; R10 log claim 10 | 2026-09-06 / 2026-09-16 | 2026-09-17 | yes |
| 11 | Hotel-RevPAR readthrough to ABNB: MAR/HLT RevPAR y/y vs nights y/y r 0.88 (post-2022 n 14), walk-forward RMSE ratio 0.665–0.70 vs naive (the strongest external family), but "since 2024 Airbnb's own recent growth beats every peer model"; BKNG guided Q3 room nights +3–5% vs Airbnb "low double digits"; US hotel prices ran negative for seven quarters while Airbnb's pricing residual rose — hotel ADR does not track the ADR residual | `research/notes/2026-09-06_predictive-study.md` §4; `data/processed/q3nowcast/G/G_backtest_scoreboard.csv`; `research/notes/adrq3/J_adr-pricing-residual-and-card-v2.md` §2; `05_macro` §4.8 | 2026-09-06 to 2026-09-11 | 2026-09-17 | yes |
| 12 | Model (this log, revision 2): FY26 +4.4% with **measured** Q1 +3.53 and Q2 +5.60 and Q3 assumed 5.0–6.0 implies 4Q26 **+2.69** (range +0.46 to +4.92 across the FY 4.0/4.4/4.8 × Q3 grid); AR(1) **one step** from the Q3 average +5.5 gives +4.20 and from the mid-August clean exit rate +4.4 gives +3.54 (φ 0.6, long run 2.25), average +3.87; adjustments −0.4 election week, −0.2 CR expiry, **+0.2 measured comp credit on the AR leg only** (3Q25 −1.40 vs 4Q25 −1.80) = −0.4; decomposition centre **+2.88**; blended with the unadjusted anchor (+2.69) and the base rate → published mixture 0.90 N(2.795, 2.111) + 0.10 N(0.8, 1.8), mean +2.60, sd 2.17, **P(≥4.0) 0.259, P(≤1.0) 0.232**, E[RevPAR \| ≥4] +5.31 | [datasets/r11_v2_views.csv](datasets/r11_v2_views.csv), [datasets/r11_v2_path.csv](datasets/r11_v2_path.csv), [datasets/r11_v2_joint_object.json](datasets/r11_v2_joint_object.json) | 2026-09-17 | 2026-09-17 | yes |
| 13 | No prediction market on US RevPAR exists (Polymarket and Kalshi searched in this batch's R10/R16 pulls: Polymarket returns only September DXY ladders, Kalshi has no hotel or RevPAR series); the domain anchor is the CoStar/TE forecast (claim 2) | R10 log claim 14; `../risk-dollar-weakens/sources/polymarket_search_*.json`, `kalshi_series_economics_20260917T075503Z.json` | 2026-09-17 | 2026-09-17 | no |
| 14 | Brief sensitivities: 1pt of 4Q26 nights ≈ $30M; 1pt of ADR ≈ $46M of quarterly revenue on the 3Q26 base (~$30M on 4Q26's $3,178M); FY27 EPS $0.0014 per $M of EBITDA; $1.50/share per pt of FY27 nights (fixed multiple), $4.90 (joint solve). FY line build: FY26 revenue $14,268M / EBITDA $5,098M (35.729%); FY27 $15,829M / $5,483M (34.639%) | `docs/pitch-forecasts/00_BRIEF.md`; `docs/margin-build/SYNTHESIS.md` §FY table | 2026-09-16 | 2026-09-17 | yes |
| 15 | Web recency: CoStar has not published the August 2026 monthly (the July monthly came 26 Aug; August expected ~25 Sep); the latest weekly reprint is the week ending 5 Sep (Lodging, 11 Sep); costar.com and str.com return 403 to fetchers, and a Wayback pull of str.com press releases returned nothing usable (`sources/str_wayback/` is empty) | https://lodgingmagazine.com/?s=costar (list fetched 2026-09-17); `sources/str_wayback/` | 2026-09-11 | 2026-09-17 | no |

Newest load-bearing source: the week-ending-5-Sep STR reprint (11 Sep, 6 days old) and the 10 Aug forecast (38 days old against a 130-day window; the next forecast revision is due in November — monitoring row 5).

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
11. [computed] `datasets/r11_model.py` (revision 1; retained as the audit trail)

**Revision 2 (audit response), 2026-09-17:**
12. WebFetch (no WebSearch charged): the Lodging Magazine `?s=costar` and CoStar-tag listings, then **58 individual Lodging article pages**, saved verbatim to [sources/lodging_monthly/](sources/lodging_monthly/) (09:51–10:08) with the pull index in `_index.json`. This is the retrieval A12-11 said had failed in revision 1.
13. WebFetch: the four forecast/annual pages re-saved with timestamps — `hotelnewsresource_costar_forecast_10aug2026_*.html`, `hoteldive_costar_te_raise_outlook_aug2026_*.html`, `hoteldive_costar_te_forecast_jun2026_*.html`, `hoteldive_fy2025_us_hotel_performance_*.html`, `lodging_costar_fy2023_annual.html`
14. WebFetch: web.archive.org for str.com press releases (October/November/December 2025) — **nothing usable returned**; `sources/str_wayback/` is empty and claim 8 is therefore marked "search snippet, unsaved"
15. [computed] `datasets/r11_extract_lodging_monthly.py` — parses the 58 snapshots into 28 dated monthly observations, with a per-file accept/reject report
16. [computed] `datasets/r11_model_v2.py` — base rate, FY-implied path, AR leg, joint object with B15
17. [repo] `docs/margin-build/SYNTHESIS.md` FY annual table (line-build revenue and EBITDA, for the §9 rows A12-18 said were understated)
18. [repo] `../bonus-q4-us-revpar-soft/forecasts/2026-09-17-forecast.json` and its log §5–§7 (the mirror's revision-1 mixture, adopted here in form)

WebSearch calls charged to R11: 5 of 5 (revision 1). Revision 2 added no WebSearch, only WebFetch on known URLs.

## 3. Leading Hypothesis Entities
CoStar, STR, Tourism Economics, Lodging Magazine, US hotel RevPAR, Marriott, Hilton, Labor Day, midterm elections, continuing resolution

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Summer strength (+5–8%) persists into Q4 on the soft 4Q25 base (Oct −0.9, Nov −2.3, Dec ~−2.2) | kept, the Yes path (≈0.26) | the mid-August slope (+7.3 → +4.4 → +1.7 clean, ADR +5.7 → +0.6) says the World Cup/summer premium is fading; the comp helps, but by the **measured** 0.4pp between 3Q25 and 4Q25, not by the 0.8pp revision 1 credited |
| The CoStar/TE FY26 +4.4% arithmetically implies a Q4 near +3% | kept as the anchor (0.25) | with the **measured** Q1 +3.53 and Q2 +5.60 (revision 1 used an assumed 4.5–6.0 grid), FY 4.4 and Q3 5.0–6.0 leave Q4 at **+2.69**, half a point below revision 1's +3.1; the FY number is a stale point forecast revised +1.6pp in two months (2.8 → 4.4) |
| The +0.8pp "easy 4Q25 comp" credit belongs on the whole blend | **discarded (A12-04)** | a published FY26 y/y forecast already embeds the 4Q25 base, so crediting the comp again on top of the FY-implied leg double-counts. What survives is a smaller, measured credit on the AR leg only: 4Q25 printed 0.4pp weaker than 3Q25, so a y/y AR step into Q4 faces a comp easier by exactly that much (+0.2 on the 50/50 blend) |
| Operator H2 guides (~+2.5%) are the better read | folded into the AR(1) long run (2.25) | system-wide **global** figures; US & Canada ran +5 in Q2 and +8 in July for Marriott (claim 9) |
| Midterm election week and a December shutdown repeat the 2024/2025 patterns | kept as adjustments (−0.4, −0.2) | the w/e 8 Nov 2025 got +6.2% "from a straightforward comparison" with election week 2024; Nov 2026 gives that back — one week at ~−5% over a 13-week quarter is −0.4, not the −0.7 revision 1 and the audit both used |
| Luxury-led barbell means aggregate RevPAR ≥4 while economy is flat | inside the centre | July luxury +17.7 vs economy +3.6; the aggregate is what resolves |
| The unconditional base rate is the right prior | kept at weight 0.2, not more | 1 of 9 quarters ≥ +4 since 2023Q3 — but every month since February 2026 has printed ≥ +4.0 except January, so the 2024–25 no-growth regime the base rate mostly describes is one the data have left. Weighting it above 0.3 would ignore that; dropping it entirely (0.6/0.4/0) gives 0.27, so it is not what sets the answer |
| US RevPAR is a good forecaster of ABNB Q4 nights | kept for the impact table only, at a low slope | r 0.88 in levels but decoupled since 2024 (claim 11) |

## 5. Independent Estimates
- base_rate_estimate: 0.22 — **measured**, not asserted: 1 of 9 reconstructed quarters 2023Q3–2026Q2 at ≥ +4.0% (Laplace 0.18), or 1 of 6 on the fully-snapshotted subset (Laplace 0.25); the two averaged give 0.216 (claim 6, `r11_v2_quarterly_base_rate.csv`). This is unconditional: it spans the 2024–25 no-growth regime, which 2026 has visibly left, and it is weighted 0.2 for that reason
- decomposition_estimate: 0.28 — FY-implied 4Q26 **+2.69** and the two-start AR leg **+3.87** averaged, then −0.4 election week, −0.2 CR expiry, +0.2 measured comp credit → centre **+2.88**, in the mixture form below: P(≥4) 0.284 (claim 12). Revision 1's +3.5 centre is withdrawn: it used an assumed Q1/Q2 grid and the double-counted comp credit
- anchor_estimate: 0.25 — the CoStar/TE FY26 +4.4% (10 Aug 2026) implied Q4 of **+2.69**, unadjusted, in the same mixture: P(≥4) 0.248 (claim 2); no tradable market (claim 13)
- anchor_value: 0.25 (CoStar/TE FY26 +4.4% of 10 Aug 2026 net of the measured H1 and an assumed Q3; **NO tradable market**)
- final_estimate: 0.26 (credible interval 0.17–0.40)
- final_minus_anchor: +1 point. NOT_INDEPENDENTLY_DERIVED flag noted: the decomposition shares the FY26 forecast with the anchor, and only the AR leg, the calendar adjustments and the comp credit separate them. What lifts the final above the anchor is the AR persistence of a +5–8% summer; what holds it near 0.25 rather than revision 1's 0.38 is that the FY-implied leg is computed on **measured** H1 months rather than an assumed grid, and that the comp credit is 0.2 rather than 0.8. Audit A12's independent number is 0.29; this revision lands 3 points below it and the reason is named in §10

## 6. Final Numbers
**Binary.** P(STR US RevPAR 4Q26 y/y ≥ +4.0%) = **0.26**, credible interval **0.17–0.40**.

**One published distribution, shared with B15** ([datasets/r11_v2_joint_object.json](datasets/r11_v2_joint_object.json)): 0.90 × N(+2.795, 2.111) + 0.10 × N(+0.8, 1.8), i.e. mean **+2.60%**, sd **2.17**. Its tails are
P(≥ +4.0) **0.259**, P(+1.0 < x < +4.0) **0.508**, **P(≤ +1.0) 0.232** (the mirror question B15), P(≤ 0) 0.116;
E[RevPAR | ≥ +4] = **+5.31%**, E[RevPAR | ≤ +1] = −0.25%.
Both trend parameters are solved so that **both** tails equal the 0.5/0.3/0.2 blend of the three estimates — matching only the upper tail, which is what revision 1 did, hands B15 a number this log's own blend does not imply (A12-10). Revision 1's normal N(3.517, 1.676) and its "P(≤1) = 0.07", and B15's revision-1 mixture 0.90 N(3.7, 1.6) + 0.10 N(0.8, 1.8) with P(≤1) = 0.10, are all **withdrawn**.
Extreme-probability gate: not triggered.

## 7. Sensitivity
Rows from `datasets/r11_v2_sensitivity.csv` (blended P(≥4); P(≤1) in brackets).
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Comp credit +0.2 on the blend (AR leg only, measured) | revision 1's +0.8 on the whole blend restored: **0.32** [0.21]; no credit at all (the audit's route): **0.24** [0.24] |
| Election-week −0.4 and CR −0.2 | no calendar drag: 0.32 [0.21]; election −0.7 (the audit's figure): 0.23 [0.25]; a December shutdown realised (CR row −1.0): **0.19** [0.29] |
| FY26 forecast +4.4 held through November | cut to +4.0: **0.19** [0.29]; raised to +4.8: **0.35** [0.20] |
| AR from both starts (Q3 average 5.5 and exit rate 4.4) | Q3 average only: 0.28; exit rate only: 0.24 |
| AR φ 0.6 | 0.8: 0.29; 0.4: 0.23 |
| AR long run 2.25 | 2.1 (TE FY27 as published): 0.26; 3.0: 0.27 |
| Q3 runs +5.0–6.0 (Jul 8.2, Aug ~5.5, Sep ~3) | Q3 +6.5 (September holds +6), FY held: 0.24 — a stronger September **lowers** P through the FY constraint and raises it through the AR leg, and the FY constraint wins; Q3 +4.5: 0.28. The honest read is that the FY anchor is stale, so a strong September should be taken as evidence the FY figure will be raised (row above), not as a Q4 drag |
| Trend sd 2.11 (blend-implied) | 1.4: 0.24 [0.21]; 2.2: 0.27 [0.25] |
| Shock branch 0.10 at N(0.8, 1.8) | weight 0.05: 0.26 [0.23]; 0.20: 0.27 [0.24]; centre 0.0: 0.27 [0.24] |
| View weights 0.5/0.3/0.2 | 0.6/0.3/0.1: 0.27 [0.20]; 0.4/0.3/0.3: 0.25 [0.26]; base rate dropped: 0.27 [0.17] |
| Joint bull (Q3 6.5, FY 4.8, no drag, φ 0.8, lr 3.0) | **0.44** |
| Joint bear (Q3 4.5, FY 4.0, December shutdown) | **0.16** |

Pre-mortem ("it is 25 Jan 2027 and Q4 RevPAR printed ≥ +4%"): (1) the soft 4Q25 comp did more than the measured 0.4pp — October 2025 was −0.9% with a shutdown and hurricane-market comps, and a merely flat December 2026 against −2.2% is +2 on its own; the comp adjustment is still the least-measured input, and it is the one this revision cut; (2) group and luxury carried the aggregate (Marriott: group "turned upwards", luxury +17.7% in July) while economy stayed flat; (3) rate held at ADR +3% rather than the +0.6% of late August; (4) CoStar raised FY26 again in November, which the sensitivity says is worth +9 points on its own. ("It printed ≤ +1%"): airfares rationing air travel (TSA −3.7%), the midterm week, a CR shutdown, and the World Cup/America-250 summer premium fully unwound — the path the 0.10 shock branch prices, and the reason the lower tail is 0.23 rather than revision 1's 0.07. Asymmetry: the memo cites decelerating hotels as corroboration of an Airbnb deceleration; a strong Q4 RevPAR print would remove that line but does little to ABNB's own KPI (claim 11), so the cost of being wrong here is narrative, not model.

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| weekly (Thu) | CoStar weekly US results (Lodging reprint) | September clean weeks ≥ +5%: +0.03 per two weeks of confirmation; ≤ +2%: −0.03 |
| ~2026-09-25 | CoStar August 2026 monthly | **Append it to `us_revpar_monthly_yoy_measured.csv` by re-running the extractor, then re-run the model.** August ≥ +6%: +0.03; ≤ +4%: −0.03 |
| 2026-10-02 | Prelim memo freeze | Quote **0.26 (0.17–0.40)** with B15's mirror **0.23** as the same distribution's other tail |
| 2026-10-21 to 2026-11-03 | Hilton, Hyatt, Marriott Q3 prints; FY26 RevPAR guides | A second raise (to ≥ +3.5–4.0%): +0.05; a cut: −0.05 |
| ~2026-11-10 | CoStar/TE November forecast revision | Re-anchor on the new FY26 figure: +0.4pp on FY26 ≈ +0.09 (sensitivity row 3); −0.4pp ≈ −0.07 |
| 2026-11-03 | Midterms | No action; the −0.4 is priced |
| ~2026-11-20 | CoStar October monthly | October ≥ +4%: → ~0.45; ≤ +2%: → ~0.14 |
| 2026-12-11 | CR expiry | A shutdown: → ~0.19 (and B15 → ~0.29) |
| ~2026-12-20 | CoStar November monthly | Update the three-month mean arithmetic; two months known collapses the sd to ~0.9 |
| ~2027-01-22 | CoStar December monthly / FY2026 release | Resolve on the mean of the three months (convention 1) |

## 9. Impact
If Yes (E[4Q26 RevPAR | ≥ +4] = **+5.31%** vs the distribution mean **+2.60%**, i.e. **+2.71pp** of US hotel RevPAR; a stay-date, US-only series). Revision 1 priced a +1.7pp delta off a centre of +3.5 and then under-computed the margin and EPS rows by 2–3× (A12-18); both are corrected here against the line build (claim 14).

| Item | Delta if R11 happens | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | 0 | Q4 series; Q3 resolves first |
| 4Q26 nights (pts) | **+0.5** | RevPAR→nights slope ~0.4 on the 2023–26 co-movement × 2.71pp = 1.08, halved for the stay-date/bookings mismatch and NA's ~30% share of nights (claim 11) |
| ADR (pts) | **+0.4** | NA ADR co-moves with hotel ADR direction; the pricing residual does not (claim 11) |
| 4Q26 revenue ($M) | **+27** | 0.5 × $30M + 0.4 × ~$30M (claim 14; the ADR rate is scaled from the 3Q26 $46M to 4Q26's $3,178M base) |
| FY27 revenue ($M) | **+50** | 60% persistence of the +0.5pt into FY27 nights (+0.3pt) at ~$158M per point of FY27 growth; STR's own FY27 +2.1% is unchanged |
| FY26 adj. EBITDA margin (pp) | **+0.12** | held: (5,098 + 27) / (14,268 + 27) = 35.852% vs 35.729% |
| FY27 adj. EBITDA margin (pp) | **+0.21** | held: (5,483 + 50) / (15,829 + 50) = 34.844% vs 34.639% |
| FY27 EPS ($) | **+0.07** | ΔRevenue × $0.0014 per $M, the held convention used for the margin row above (A12-02: 0.66 is pp-of-margin per point of revenue and must not be applied a second time as a dollar rate). On the flex convention (0.42pp/pt) the pair is +0.13pp / +$0.04 |
| Stock ($/share) | **+2.0** | +0.3pt of FY27 nights × $1.50 (fixed multiple) = $0.45, or × $4.90 (joint solve) = $1.47, plus ~$1 for the loss of the memo's "hotels are decelerating" corroboration into the 5 Nov and February narratives |
| **EV = P × impact** | **0.26 × $2.0 ≈ $0.5/share** | |
| Materiality | **Immaterial** (EV under $1/share, on both the fixed-multiple and joint-solve readings). The memo can drop the hotel line as a risk; keep the weekly STR tape as an alt-data monitor. B15's mirror is the same distribution's other tail: EV −0.23 × $2.5 ≈ −$0.6/share, also immaterial | |

## 10. Revision notes
| Change | Finding | Effect |
|---|---|---|
| The base rate is no longer the hand-entered list at `r11_model.py:36`. 58 Lodging Magazine reprints of the CoStar monthly release were fetched and saved; `r11_extract_lodging_monthly.py` parses **28 dated monthly observations** out of them (rejecting 30 weekly/P&L pages, with the reason logged per file) and the quarters are computed from those. Claim 4 and claim 6 replace claim 10 of revision 1; B15's "6 of 13 ≤ +1" is withdrawn with it | **A12-03** | base rate ≥+4: "1 of 13" (unsourced) → **1 of 9** measured, Laplace 0.18–0.25; base-rate estimate 0.20 → 0.22 |
| The +0.8pp easy-comp credit is removed from the blend. What replaces it is measured: 3Q25 printed −1.40 and 4Q25 −1.80, so the y/y comp into Q4 is easier by 0.4pp, credited to the **AR leg only** (+0.2 on the blend). Both directions are now in §7 | **A12-04** | centre +3.52 → **+2.88**; the single largest move in the revision |
| The FY-implied leg uses the **measured** 2026 Q1 (+3.53) and Q2 (+5.60) months instead of revision 1's assumed 4.5–6.0 grid | A12-03 / A12-11 | FY-implied Q4 +3.14 → **+2.69** |
| R11 and B15 publish one distribution. Its two trend parameters are solved so that **both** tails match the three-view blend, not just R11's | **A12-10** | P(≤1): R11 said 0.07, B15 said 0.10 → **0.232**, one number in both logs |
| The anchor is re-cited to the dated repo note as primary, with four timestamped trade-press snapshots saved as secondary; claim 8 (October 2025 −0.9%, "declines continue throughout December") is marked "search snippet, unsaved" because str.com 403s and the Wayback pull returned nothing | **A12-11** | `sources/` no longer empty: 66 files; one claim explicitly downgraded |
| The AR leg is labelled **one step** in §5, in claim 12 and in the JSON field; φ and the long run are stated as hand-set and bracketed (φ 0.4–0.8, lr 2.1–3.0 in §7); a second start from the mid-August clean exit rate (+4.4) is added because the Q3 average embeds July's World Cup month | **A12-17** | AR leg +4.10 → **+3.87**; label corrected |
| §9 margin and EPS rows recomputed against the line build; the FY27 EPS row uses ΔRevenue × $0.0014 once, with the flex alternative stated | **A12-18**, A12-02 | FY26 margin +0.03 → **+0.12**; FY27 +0.05 → **+0.21**; EPS +0.01 → **+0.07**; verdict unchanged |
| Election-week drag cut from −0.7 to **−0.4** (one week at ~−5% over a 13-week quarter), against both revision 1 and the audit | — (this revision's own correction) | +0.03 on the final; row added to §7 |
| Claim 9 now states that the operator series and the repo's only quarterly hotel panel are **operator, global, system-wide** — a different object from all-US STR | A12-03 (its verification note) | prevents the panel being mistaken for a US quarterly series |
| Final 0.38 → **0.26** (0.25–0.52 → 0.17–0.40); E[x \| ≥4] 5.2 → 5.31 | A12-03/04/10/11/17 | −12 points |
| Housekeeping: `datasets/us_revpar_monthly_yoy_reconstructed.csv` is an intermediate from this revision's first pass, in which the monthly series was still transcribed by hand. It is **superseded by `us_revpar_monthly_yoy_measured.csv`**, which is machine-parsed, and is referenced by nothing; it is left on disk only as the audit trail and must not be quoted | — | none |

**On the 3-point gap to the audit's 0.29.** The audit's route takes the anchor at +3.1 (revision 1's FY-implied figure, computed on the *assumed* Q1/Q2 grid), the AR at +4.1 (the single Q3-average start), blends to +3.6, applies −0.7 and −0.2 and no comp credit for +2.7, then puts the centre back up to +3.0 "because the AR long run is depressed by a World Cup comparison that has nothing to do with 4Q26". Two of those inputs are superseded by measurement in this revision: the FY-implied leg is +2.69 on the actual H1 months, not +3.1, and the election drag is −0.4 on the one-week arithmetic, not −0.7. The World Cup argument the audit uses to add back 0.3 is accepted, but it belongs in the long run, where §7 prices it (lr 2.1 → 3.0 is worth +0.01 on the final), not as a free add-on to the centre. Net, this log's centre is +2.88 against the audit's +3.0, and the final is 0.26 against 0.29 — inside the 10-point band, with the difference named.

RESUME: the next agent should (1) re-run `r11_extract_lodging_monthly.py` after the **August 2026 monthly (~25 Sep)** and again after each later release — the extractor is written so that dropping a new snapshot into `sources/lodging_monthly/` is the whole update; (2) try once more to source the nine months the parse is missing (2023-09/10/12, 2024-02/03/10/11, 2025-12, 2026-03) so that 2023Q4, 2024Q1 and 2024Q4 enter the base rate and March 2026 stops being a hand-carried figure; (3) attack the two remaining judgements — the −0.4 election-week drag and the 0.10 shock branch, which between them set the lower tail B15 now publishes; (4) re-anchor on the **CoStar/TE November revision**, the single highest-value update on the calendar (±0.4pp on FY26 ≈ ∓0.08 on the final).
