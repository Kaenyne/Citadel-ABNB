# WS04: External and alternative-data signals for each cost line and below-EBITDA item

**Date:** 13-14 Sep 2026 (pulls 04:35-06:10 UTC 14 Sep). Author: Claude Code (Fable 5.1) for Krish's margin build run.
**Slug:** `04_alt_signals`. Script `analysis/src/margin_build/04_alt_signals/run.py` (rebuilds everything from raw; exit 0; ~20 s).
**Question:** which external series explain or lead a cash cost line, adj. EBITDA margin, or interest income, so that M4 (alt-augmented
line model) and M7 (below-EBITDA bridge) have real inputs. Wide net; most were expected to fail, and most did.

## 1. Bottom line

1. **One family of signals is unambiguous: short rates explain interest income.** y/y change in the 3-month T-bill against y/y change
   in quarterly interest income (SEC XBRL `InvestmentIncomeNonoperating`, Q4 filled from the FY frame): r +0.83 contemporaneous, +0.59
   led one quarter, n = 18 (1Q22-2Q26); 1-year UST r +0.88 / +0.79 / +0.50 at leads 0/1/2; fed funds and SOFR +0.77. All survive the recent
   window (1Q24-2Q26, n = 10), the recency weighting, and the control for revenue growth (partial r +0.83 to +0.90). The mechanism is
   plain and the M7 rule needs one parameter: **interest income per quarter = 0.86 x 3m T-bill (quarter average, annualised) x average of
   (cash + short-term investments + funds held for clients) / 4.** The realised ratio of implied yield to the 3m T-bill is 0.86 on
   1Q23-2Q26 (n = 14, range 0.77-0.97) and 0.88 on the last four quarters. 2Q26 reads: yield 3.13% on a $23.4bn average base, $183m.
2. **One marketing signal survives every filter, and it is contemporaneous, not leading.** Airbnb's share of category search
   (Google Trends "airbnb" / ("airbnb" + "booking.com" + "expedia" + "vrbo"), same-payload stitched values from the repo's 6 Sep pull)
   y/y against **S&M cash per night** y/y: r -0.64 (US) and -0.57 (worldwide), n = 18, lead 0; recent window -0.59 / -0.56 (n = 10);
   partial r controlling for nights growth -0.64 / -0.56. Sign was pre-registered "either"; the observed sign says S&M per night rises when
   Airbnb's search share falls (2025-26: share -5 to -11% y/y, S&M per night +7 to +22% y/y). Read it as the marketing response to share
   loss, which is what management has been saying in words. It is knowable before the print (Trends is daily), so it is a nowcast
   input for the quarter just ended, not a lead. The level series ("airbnb" alone) does nothing once volume is controlled (partial -0.10).
3. **Open roles on careers.airbnb.com are the most promising labour signal but the sample is too thin to score.** Wayback captures give
   19 quarterly readings 2019Q1-2026Q1 with gaps, so y/y pairs against product development cash are n = 6-7: r +0.90 (lead 0), +0.96
   (lead 2), partial +0.87 / +0.98. Direction and lead are what a hiring pipeline should show, and the 2Q26 product development step
   (+$41m q/q) followed the 1Q26 reading of 237 open roles (the highest since 2019). Verdict stays "logged, not promising" on the
   pre-registered rule because n < 14; the fix is mechanical (parse all 92 home-page captures monthly, and the 59 positions-page captures),
   see RESUME.
4. **Everything else fails, and the failures are informative.** BLS wage and employment indices for software publishers, computer
   systems design, information-sector hourly earnings, the ECI and SF Bay CPI have |r| < 0.5 against product development and G&A at every
   lead (n = 18). PPIs for data hosting and insurance brokerage do nothing for cost of revenue or ops & support. App-store rating
   velocity (Apple, n = 9-11; Google Play, n = 12-14) is unstable in sign. Glassdoor, Trustpilot and Sitejabber counts exist only to 2023
   (bot walls after), n <= 5. The AI-support step dummies (Apr 2025 US launch; Feb 2026 "one third"; May 2026 "over 40%") read r -0.45,
   -0.21, -0.18 against ops & support cash growth, the right sign but not near the line, and the 2026 steps have only one or two
   post-event quarters. Peer marketing (BKNG advertising, EXPE SG&A) correlates with Airbnb's S&M dollars (r +0.63-0.65) only because
   both track nights: partial r is 0.04 and -0.14.
5. **Macro to margin is entirely the volume channel.** Hotel RevPAR (MAR, HLT) led one quarter has r +0.83 / +0.84 with margin y/y and
   TSA throughput +0.91, but the partial r after controlling for revenue growth is -0.54, -0.52 and -0.02. For M6 that is the useful
   statement: cycle series belong on the revenue side; there is no separate cost-flex signal in them.

Counts: 58 series in the panel, 75 catalogue rows (53 pulled, 9 partial, 12 unreachable, 1 out of rules), **1,146 tests** (573 series x
line x lead pairs on two windows). Full-window "candidate" on the pre-registered rule: 105 of 573 (most are nights and margin targets
in the common 2022-26 deceleration); survive the recent window too: 21; survive the volume control as well: **9**, of which 7 are
rates -> interest income and 2 are Trends share -> S&M per night. Free parameters: none in the panel or the tests (each test is one
correlation; the pass line was fixed before running); the M7 yield rule has one (0.86).

## 2. Pre-registered pass line (from the prompt, fixed before any test ran)

Pearson r between the signal's y/y change and the matching cash cost line's y/y change (per night for cost of revenue, ops & support and
S&M; also cost of revenue as % of GBV), contemporaneous and led 1-2 quarters, over the longest window the cash lines allow (cash lines
start 1Q21, so y/y pairs run 1Q22-2Q26, n <= 18), and the same against adj. EBITDA margin (y/y change in pp) and, for macro series, nights.
|r| >= 0.5 with n >= 14 and the expected sign = "candidate"; otherwise "logged, not promising"; n < 4 or a constant = "insufficient n".
Added per the run brief (also fixed before running): the same r on 1Q24-2Q26 (n <= 10, "recent-window pass" at |r| >= 0.5, n >= 8),
an exponentially recency-weighted r (half-life 4 quarters), and a partial r controlling for nights y/y (revenue y/y for margin and
interest income). `candidate_both` = candidate on the full window and pass on the recent window; `candidate_ex_volume` additionally
requires the partial r to keep |r| >= 0.5 with the right sign. Expected signs are in `run.py` (`SIGN`); "either" was used where the
mechanism is two-sided (brand demand vs marketing spend; app-store rank).

## 3. What ran (exact commands, worktree root)

```
python  analysis/src/margin_build/04_alt_signals/pull_fred.py --pull            # 30 ids; 21 pulled, 9 unreachable (404); +5 alternates found by curl loop
curl -s "http://web.archive.org/cdx/search/cdx?url=<page>&output=json&from=2018&filter=statuscode:200&collapse=timestamp:6&fl=timestamp,original,statuscode,length" -o wayback/cdx_<page>.json
python  analysis/src/margin_build/04_alt_signals/pull_wayback.py --pull careers_home careers_positions linkedin glassdoor appstore trustpilot playstore sitejabber
curl -s -A "Mozilla/5.0 citadel-abnb research ksurapaneni@ufl.edu" https://www.tsa.gov/travel/passenger-volumes/<year> -o tsa/tsa_<year>.html   # 2019-2026 + current
py -3.13 analysis/src/margin_build/04_alt_signals/pull_lseg_peers.py --pull       # TR.Revenue, TR.TotalOperatingExpense, TR.CostOfRevenueTotal, TR.EBITDA (BKNG, EXPE, ABNB, TRIP) FQ 2019-2026
py -3.13 analysis/src/margin_build/04_alt_signals/pull_lseg_peers_sm.py --pull    # TR.SGAExpenseTotal, TR.AdvertisingExpense, TR.F.EmpFTEEquivPrdEnd
python  analysis/src/margin_build/04_alt_signals/run.py
```

One-off derivations recorded here because they are not in `run.py`: `tsa/tsa_daily_parsed.csv` (regex over the `<tr>` rows of the
year pages, 2,810 days 2019-01-01..2026-09-10); `wayback/_careers_parse_raw.csv` (count strings "N roles" / "N Open Positions" /
"N open jobs" from each careers capture); `xbrl/abnb_xbrl_below_ebitda_facts.csv` (17 tags from `data/raw/xbrl/ABNB_companyfacts.json`);
10-K sentence extraction with decimal-safe regex over `data/raw/filings/abnb_10k_FY2020..FY2025.htm` into `misc/tenk_annual_drivers.csv`
(54 rows, one source locator each); `misc/events_step_dummies.csv` (10 events with URL).
Google Trends were **not** re-pulled: pytrends on `py -3.13` fails (`Retry.__init__() got an unexpected keyword argument
'method_whitelist'`, urllib3 2.x incompatibility); the repo's 6 Sep 2026 weekly pull (`data/processed/overnight/08_trends_weekly.csv`,
9 terms, WW + US, to 2026-09-06) was used instead.

## 4. Catalogue (every series attempted)

Full table with status, coverage, source and knowable rule: `data/processed/margin_build/04_alt_signals/04_signal_catalogue.csv` (75 rows).
Summary by target line:

| Target | Pulled (n quarters in panel) | Partial | Unreachable / out of rules |
|---|---|---|---|
| Interest income (M7) | DTB3, DGS1, FEDFUNDS, SOFR, ECBDFR (quarter means); funds held for clients, cash, short-term investments (XBRL, 22) | | |
| Product dev, G&A | CES software publishers emp., computer systems design emp., information AHE, ECI wages, SF Bay CPI (18 y/y pairs); 10-K year-end employees (6 annual) | careers open roles (19 obs, 6-7 y/y pairs); Glassdoor review count (10 obs to 2023Q3); layoffs.fyi (events only); LinkedIn (2 usable captures, member self-reports, not headcount); BKNG/EXPE FTE (annual only) | CES AHE software publishers / computer systems design, JOLTS information openings and layoffs, PPI custom programming (FRED 404, 24 alternates tried) |
| Ops & support | CES business support services emp.; PPI insurance brokerages; Apple App Store rating velocity (22 obs); Google Play rating velocity (21 obs); AI-support step dummies E05/E07/E08 | Trustpilot (8 captures, 5 velocities, to 2023Q3); Sitejabber (5 captures to 2021Q4); 10-K contingent workers (3 annual) | BBB (no 200 captures); Downdetector (live chart only, out of rules); PPI call centres (404) |
| Cost of revenue | PPI data hosting (two series); USD/EUR; broad dollar; funds held (pay-in proxy); events E02/E03/E04/E06/E09; 10-K chargebacks (6 annual), hosting commitment (5 annual) | | |
| Sales & marketing | Trends "airbnb" WW/US and Airbnb share of category search WW/US (31 quarters); BKNG/EXPE opex ex-CoR, SG&A, BKNG advertising y/y (LSEG, derived y/y only); App Store travel rank (23) | Inside Airbnb median-city listings y/y (5 quarters, composition-limited); fee event E01 | Meta Ad Library report (socket hang-up; JS; political ads only); Google Ads Transparency (JS SPA) |
| Macro (M6) | UMich sentiment, real DPI, real PCE, CPI, unemployment, initial claims, accommodation employment, TSA throughput (31), MAR/HLT RevPAR (repo, 22) | | |

`knowable_from` per observation is in `04_signal_knowable_from.csv`: Wayback series carry the capture date; XBRL and 10-K series the
filing date; FRED series quarter end + a publication lag (1 d daily rates/FX, 7 d CES/claims, 14 d CPI/PPI, 30 d ECI/DPI/PCE);
LSEG peer series quarter end + 40 d; Trends and TSA quarter end + 1 d.

## 5. Test table

Every test: `04_signal_tests.csv` (1,146 rows; columns series, family, line, lead_q, window, n, r, r_recency_hl4, r_partial_volume,
partial_ok, sign_expected, sign_ok, verdict, candidate_both, candidate_ex_volume). Selected rows (full window 1Q22-2Q26; `r_rec` is the
1Q24-2Q26 window; `r_part` controls for nights y/y, or revenue y/y for margin and interest income):

**Survivors (candidate on both windows and after the volume control)**

| series | line | lead | n | r | r recency | r_rec (n=10) | r_part | verdict |
|---|---|---|---|---|---|---|---|---|
| rate_ust1y | interest_income | 0 | 18 | +0.88 | +0.87 | pass | +0.90 | candidate_ex_volume |
| rate_tbill3m | interest_income | 0 | 18 | +0.83 | +0.82 | pass | +0.83 | candidate_ex_volume |
| rate_ust1y | interest_income | 1 | 18 | +0.79 | +0.77 | pass | +0.78 | candidate_ex_volume |
| rate_fedfunds | interest_income | 0 | 18 | +0.77 | +0.76 | pass | +0.77 | candidate_ex_volume |
| rate_sofr | interest_income | 0 | 18 | +0.77 | +0.76 | pass | +0.77 | candidate_ex_volume |
| rate_tbill3m | interest_income | 1 | 18 | +0.59 | +0.62 | pass | +0.59 | candidate_ex_volume |
| rate_ust1y | interest_income | 2 | 18 | +0.50 | +0.54 | pass | +0.51 | candidate_ex_volume |
| trends_airbnb_share_us | sm_cash_per_night | 0 | 18 | -0.64 | -0.64 | -0.59 | -0.64 | candidate_ex_volume |
| trends_airbnb_share_ww | sm_cash_per_night | 0 | 18 | -0.57 | -0.62 | -0.56 | -0.56 | candidate_ex_volume |

**Passed both windows but not the volume control (the deceleration look-alikes)**

| series | line | lead | n | r | r_rec | r_part | reading |
|---|---|---|---|---|---|---|---|
| hotel_hlt_revpar_yoy | margin | 1 | 18 | +0.84 | +0.69 | -0.52 | volume channel only |
| hotel_mar_revpar_yoy | margin | 1 | 18 | +0.83 | +0.67 | -0.54 | volume channel only |
| unemployment_rate | margin | 2 | 18 | -0.65 | -0.30 | +0.38 | fails recent window sign, partial wrong sign |
| emp_accommodation | sm_cash_per_night | 0 | 18 | -0.52 | pass | -0.47 | just under the line |
| event_E03 (AWS IPv4) | margin | 1 | 18 | -0.57 | pass | -0.14 | a 2024 step dummy tracking the 2024-25 margin slide; not causal |
| event_E06 / E09 (AWS GPU cut; hosting commitment) | cor_cash_per_night | 1-2 | 18 | +0.54 | pass | +0.48 | same step (mid-2025 / early 2026), sign wrong for E06 |

**Targeted alt series that did not pass (own line)**

| series | line | best lead | n | r | r_rec | r_part | why it fails |
|---|---|---|---|---|---|---|---|
| careers_open_roles | pd_cash | 2 | 7 | +0.96 | +0.97 (n=4) | +0.98 | n < 14 (capture gaps) |
| careers_open_roles | ga_cash | 2 | 7 | -0.71 | -0.67 | -0.78 | n, and sign against expectation |
| appstore_new_ratings_per_day | ops_cash | 2 | 11 | +0.68 | -0.72 (n=4) | +0.38 | n < 14, sign flips in recent window |
| playstore_ratings_new_per_day | ops_cash | 2 | 14 | +0.28 | -0.12 | +0.09 | no relationship |
| emp_business_support_services | ops_cash | 2 | 18 | +0.69 | +0.01 | +0.33 | recent window 0, partial 0.33 |
| ppi_insurance_brokerage | ops_cash | 2 | 18 | -0.50 | -0.04 | -0.37 | wrong sign, recent window 0 |
| ppi_data_hosting | cor_cash_per_night | 0 | 18 | +0.46 | +0.33 | +0.32 | under the line at every lead |
| fx_usd_per_eur | cor_cash | 0 | 18 | -0.55 | +0.38 | -0.14 | sign flips in recent window; partial 0 |
| event_E05 (AI agent Apr 2025) | ops_cash | 0 | 18 | -0.45 | -0.15 | -0.32 | right sign, under the line |
| event_E07 / E08 (AI 1/3, 40%) | ops_cash | 0 | 18 | -0.21 / -0.18 | ~0 | -0.14 | 1-2 post-event quarters |
| event_E02 (Apr 2022 interchange) | cor_cash_pct_gbv | 0 | 18 | +0.72 | n/a (constant) | +0.54 | single 2022 step; constant on recent window |
| emp_software_publishers / emp_computer_systems_design / ahe_information / eci_wages / cpi_sf_bay | pd_cash, ga_cash | any | 18 | |r| <= 0.49 | | | no relationship at any lead |
| peer_bkng_advertising_yoy | sm_cash | 0 | 18 | +0.65 | +0.43 | +0.04 | tracks nights, not Airbnb's spend decision |
| peer_expe_sga_yoy | sm_cash | 0 | 18 | +0.63 | +0.09 | -0.14 | same |
| trends_airbnb_ww (level) | sm_cash | 0 | 18 | +0.54 | +0.46 | -0.10 | volume channel |
| tenk_employees_year_end | pd_cash | 2 | 5 | +0.31 | | | annual; n = 5 |
| glassdoor / trustpilot / sitejabber / contingent workers / hosting commitment / ia_listings | | | <= 5 | | | | insufficient n |

**Macro vs margin, lead 1 (for M6):** initial claims -0.72 (partial +0.57, wrong sign), real PCE +0.83 (partial +0.25), TSA +0.91
(partial -0.02), accommodation employment +0.71 (partial -0.32), CPI +0.51 (partial -0.43), UMich -0.12, real DPI -0.39. Nothing in
macro explains margin beyond what it explains in revenue.

## 6. What was unreachable and why

- FRED 404s (id not on FRED or renamed after the NAICS 2022 revision): CES software-publisher and computer-systems-design hourly
  earnings, JOLTS information openings/layoffs, PPI custom programming, PPI call centres, CES business-support hourly earnings;
  24 alternative ids tried, 5 found (CUURA422SA0 SF CPI, PCU518210518210 hosting PPI, CES6056140001 business support employment, ICSA,
  CUUSA422SA0). Not blocking: the found labour series show nothing anyway.
- Meta Ad Library report: socket hang-up on fetch; in any case the public report covers only political/issue ads in the US. Google
  Ads Transparency Center: JS single-page app, no figures in static HTML, no useful archive. Marketing spend intensity therefore has no
  third-party observation in this package; the Trends share series is the substitute.
- BBB profile: no 200 captures for the URL pattern. Downdetector: captures exist but the page is a live 24-hour chart, no history.
- LinkedIn company page: 11 captures, 2 with a count, and the count is LinkedIn member self-reports (44,959 in 2024Q4; 55,686 in
  2025Q2, against 7,300-8,200 employees), so it measures hosts and contractors, not headcount.
- Glassdoor: counts to 2023Q3 (866 -> 2,465 reviews), then bot-wall pages. Trustpilot: 4,606 (Sep 2019) -> 11,561 (Sep 2023), then
  nothing parseable. Sitejabber: 1,011 -> 1,593 (2019-2021). None reaches n = 14.
- Google Trends re-pull: pytrends broken on the 3.13 environment (see section 3); the repo pull from 6 Sep is a week old, fine for a
  quarterly panel.
- Common Crawl fallback was not needed for careers pages (Wayback has 92 home-page and 59 positions-page captures 2019-2026).
- WS01's `01_gaps.csv` did not exist when this package started or finished; the prompt's candidate list was used.

## 7. 10-K driver facts pulled for M1/M4/M7 (annual, `misc/tenk_annual_drivers.csv`, 54 rows with locators)

- Payment processing costs (merchant fees + chargebacks): $837.0m (2019), $600.2m (2020), $844.4m (2021), 2-3% of GBV; merchant-fee
  increases +$313.9m (2022), +$163m (2023), +$173m (2024), +$188m (2025). Chargeback expense $124.7m (2020), $83.8m, $119m, $130m,
  $96m, **$67m (2025)**: falling $29-34m a year since 2023 while GBV grows, worth ~0.1 pp of margin a year.
- Cloud / data hosting cost increases +$24.9m (2022), +$31m, +$26m, +$27m (2025). Hosting commitment remaining: $1.2bn through 2027
  (end-2020), $941.7m, $842m, $672m (end-2024), then **$1.7bn through 2031** (end-2025): the committed run-rate moves from ~$224m/yr
  (672/3) to ~$283m/yr (1,700/6), +26%, the clearest forward statement about the AI-compute line in the filings.
- Ops & support: third-party community support personnel +$130.7m (2022), +$105m (2023), customer relations +$25m (2024); host
  liability insurance +$29.8m, +$16m, +$25m, +$14m (2022-25). Contingent support workers ~11,000 (end-2022 and end-2023); the 13,000
  figure for end-2025 comes from a web summary of the 2Q26 10-Q and must be verified in the filing before use.
- Headcount: 5,597 / 6,132 / 6,811 / 6,907 / ~7,300 / ~8,200 (end-2020..end-2025); 2025 +12%, with product development payroll
  +$293m, S&M payroll +$121m, G&A payroll +$51m. Call statements: headcount growth planned 2-4% (4Q22), ~4% (3Q23), ~1% actual in 2023
  (4Q23); the 2025 $200m investment "a good portion headcount" (2Q25).
- Interest income $721m (2023), $818m (2024), $705m (2025), attributed by management to rates and balances only.

## 8. Corrections to existing work

None required. Two observations for the census: `data/processed/overnight/08_supply_index_quarterly.csv` is empty for 2021-2023
(zero components), so it cannot serve as a supply signal; and the repo's `08_trends_tests.csv` finding ("search does not forecast the
print") is consistent with this note: the level series does not, the share series explains S&M per night contemporaneously, which is a
different claim.

## 9. For the model

| name | value | unit | source | use |
|---|---|---|---|---|
| `interest_income_yield_ratio` | 0.86 (n = 14, 1Q23-2Q26; last-4 0.88) | ratio of implied annualised yield to 3m T-bill quarter average | `04_interest_income_yield_diagnostic.csv` | M7: interest income = 0.86 x DTB3 x avg(cash + STI + funds held) / 4 |
| `earning_base_2Q26` | 24,293 at end-2Q26 (funds held 12,224 + cash 6,821 + short-term investments 5,248); 23,424 average 1Q26-2Q26 | USD m | XBRL | M7 base; funds held is seasonal (peaks 2Q, troughs 4Q) so use the quarter average |
| `rate_tbill3m` 2026Q3 to date | 3.74 (1y UST 4.06; fed funds 3.63) | pct, quarter average through 11 Sep | FRED DTB3/DGS1/FEDFUNDS, panel | M7 3Q26: 0.86 x 3.74% x ~$21-22bn / 4 = ~$170-175m |
| `trends_airbnb_share_us`, `_ww` | 2Q26 52.5 / 61.8 (y/y -9.2% / -10.9%); 3Q26 to 6 Sep 53.5 / 64.5 (y/y -1.2% / +0.4%) | pct of category search | panel | M4: S&M per night y/y = a + b x share y/y (b < 0; fit on 18 quarters; r -0.64). 3Q26 share stabilised, so the share signal points to a smaller S&M-per-night y/y step in 3Q26 than in 1H26 (+15-22%) |
| `careers_open_roles` | 237 (1Q26; 203 4Q25; 215 2Q25; 180 3Q24) | open roles | Wayback careers.airbnb.com | M4 (product dev, with lead 2) once monthly parse lifts n |
| `event_E05/E07/E08` | step dummies 2025Q2, 2026Q1, 2026Q2 | 0/1 | `misc/events_step_dummies.csv` | M1/M4 ops & support: use as a prior on per-night decline, not as fitted regressors (n too small) |
| `hosting_commitment_run_rate` | 283 vs 224 | USD m per year | 10-K FY2025 vs FY2024 | M1 cost of revenue: hosting line +26% committed floor |
| `chargeback_expense` | 67 (2025), -29 y/y | USD m | 10-K FY2025 | M1 cost of revenue: chargebacks keep falling ~$30m/yr |
| Panel | `04_signal_panel_quarterly.csv` (2019Q1-2026Q3 x 58 series + 12 targets), `04_signal_knowable_from.csv` | | | M4 inputs, PIT via knowable_from |

Not to use: wage/employment indices, PPIs, app-store velocity, peer marketing, macro-to-margin. Every one is "logged, not promising"
on the pre-registered rule, and the macro-to-margin correlations are volume in disguise.

## 10. For the 5 Nov card

- Interest income 3Q26 ~$170-175m (vs $180m 3Q25): rates lower y/y (3m T-bill 3.74% vs 4.10%) on a larger base. Below-the-line, EPS-relevant.
- The one alt reading that bears on a cost line for 3Q26: Airbnb's search share stopped falling in 3Q26 (US -1.2% y/y through 6 Sep vs
  -9.2% in 2Q26). Historically that goes with a smaller S&M-per-night y/y increase; it does not say S&M dollars fall.
- TSA 3Q26 quarter-to-date is partial (through 10 Sep) so its -22.8% y/y in the panel is an artifact of the missing days; do not read it.

## RESUME

Next agent: (1) lift the careers series to n >= 14 by parsing all 92 `careers.airbnb.com/` captures and all 59 `/positions/` captures at
monthly spacing (extend `pull_wayback.py` with a `--monthly` option; the count regex in `run.py` already handles the three page
generations), then re-run the pd_cash tests; if r stays above +0.5 at lead 2 with n >= 14 it becomes an M4 input. (2) Verify the
13,000 contingent-worker figure in the 2Q26 10-Q before quoting it. (3) M7 should take the interest-income rule (0.86 x DTB3 x earning
base) and backtest it point-in-time at the guide dates; the diagnostic CSV has every quarter. (4) M4 should take only the Trends share
series (S&M per night, lead 0) and the AI step dummies (as priors) from this package; the rest is logged as failed. (5) If WS01's
`01_gaps.csv` appears with items not on the prompt's list, re-run the pull scripts for those only; nothing here needs a full re-pull.
`python analysis/src/margin_build/04_alt_signals/run.py` rebuilds all outputs from raw in ~20 s.
