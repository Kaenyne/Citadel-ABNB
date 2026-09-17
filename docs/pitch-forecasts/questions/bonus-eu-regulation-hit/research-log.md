# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable). Batch A15 (B04, B05, B06, B07). Reproduction: the base rate is a Poisson count from `datasets/qualifying_events_trailing_24m.csv`; the decomposition is the product in section 5; the market-size gate is `datasets/eurostat_country_shares_scaled_to_emea.csv` plus the city anchors in claim 3.

## 0. Metadata
- question_name: bonus-eu-regulation-hit
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § B05)
- type: binary
- run_mode: initial
- run_date: 2026-09-17
- open_date: 2026-09-17
- close_date: 2027-02-11
- resolution_date: 2027-02-11
- scoring: spot
- cp_visible: no
- cp_value: n/a
- revision: 1
- agent: fable
- batch: A15

## 0b. Question (verbatim)
### Title
By 11 Feb 2027, will a new short-term-rental restriction take effect or be enacted in an EU/UK city or country whose Airbnb nights exceed 1% of EMEA nights (e.g., a Barcelona-style licence withdrawal, a national registration regime with removal of unregistered listings, or the EU Affordable Housing Act with binding STR caps)?
### Resolution Criteria
**Type.** Binary. **Resolution.** Yes if enacted (not proposed) with an effective date on or before 30 Jun 2027 and the affected market ≥1% of EMEA nights by the team's regional panel. Resolution 11 Feb 2027.
### Fine Print
None beyond the resolution sentence. Conventions adopted (each priced in section 5 and section 7):
1. "Short-term-rental restriction" = a binding rule that reduces permitted STR supply or activity: a cap on nights, a ban or zone ban, a moratorium on new licences or registrations, a licence non-renewal, a registration regime whose enforcement removes non-compliant listings, or a principal-residence requirement. Tax changes, data-sharing rules, safety/operating standards and platform fines alone do not count. The "e.g." list in the title is illustrative, not a magnitude floor.
2. "Enacted" = adopted by the competent body (statute, decree, council vote, joint ministerial decision, commencement regulations), not proposed, drafted or announced. The measure must be enacted or take effect between 17 Sep 2026 and 11 Feb 2027 (a measure enacted before 17 Sep whose effective date falls in the window also counts: "take effect").
3. An extension of an expiring freeze by a new decision counts as newly enacted (it is a fresh act of the competent body that restricts supply for a new period).
4. Market size: the team's regional panel gives EMEA ≈ 40% of nights but no city shares; the gate is applied with the team's exposure anchors: national measures qualify in FR, ES, IT, DE, EL (Greece), PT, PL, HR, AT and the UK (each ≥ 2% of EMEA); Paris (~2.5%), London (~2%), Rome (~1.5%), the Canary Islands (~2.2%) qualify; Barcelona (~0.5%), Madrid (~0.7%), Lisbon (~0.55%), Athens (~0.5%), Amsterdam (~0.35%), Florence (~0.4%), Ireland (~0.7%), the Netherlands (~1.0%, borderline) and the Balearics (~1.0%, borderline) do not qualify on a city/region-only measure. A national instrument that restricts only one sub-1% city (the Greek Athens/Thessaloniki freeze) is treated as failing the gate; the alternative reading is priced in section 7.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Airbnb EMEA nights share estimate 39.6-40.0% of global nights (2Q26); EMEA revenue 40% of 2Q26 revenue ($1,425M of $3,608M) | data/processed/overnight/10_regional_panel_quarterly.csv (emea_nights_share_est_pct); data/raw/regulatory/quantification/abnb_2026q2_10q.html | 2026-08-06 | 2026-09-17 | yes |
| 2 | Eurostat four-platform nights 2025 shares of EU27: FR 22.3%, ES 19.9%, IT 14.6%, DE 7.2%, EL 5.5%, PT 5.2%, PL 4.7%, HR 4.4%, AT 2.6%, BE 1.4%, HU 1.4%, CZ 1.3%, NL 1.25%, IE 0.9%; scaled by 0.8 (EU27 ≈ 80% of EMEA, the rest UK, CH, NO, Turkey, Middle East, Africa) to EMEA shares | data/processed/eurostat_platform_nights_by_country.csv; datasets/eurostat_country_shares_scaled_to_emea.csv | 2026-09-05 | 2026-09-17 | yes |
| 3 | Team exposure anchors: Paris ≈ 1.0% of global GBV, London ≈ 0.8%, Rome ≈ 0.6%, Ireland ≈ 0.4% of global revenue, Spain ≈ 6% of global revenue, Netherlands 1.3% and Portugal 5.2% of EU platform nights; Canary Islands 48,356 of Spain's 341,001 INE tourist dwellings (14%), Balearics 21,304 (6%); Inside Airbnb June 2026 listing counts Paris 77,679, London 92,799, Madrid 22,835, Lisbon 17,098, Barcelona 15,406, Athens 14,342, Florence 13,508, Amsterdam 10,465 | data/processed/abnb_regulatory_events.csv (anchor column); datasets/regulatory_market_inventory.csv | 2026-09-06 | 2026-09-17 | yes |
| 4 | Qualifying enacted measures in the trailing 24 months under conventions 1-4: Paris 90-night cap (Le Meur law, enacted Nov 2024, effective 1 Jan 2025); Spain Horizontal Property Law neighbour-approval rule (3 Apr 2025); Spain national registry plus the 65,935-ad removal order (May-Jul 2025); Canary Islands Law 6/2025 (Dec 2025); plus two marginal: Italy CIN mandatory (Jan 2025; registration without removal) and the Greek Athens freeze (national law, Jan 2025; Athens alone < 1%). Non-qualifying on the gate: Malaga, Madrid, Lisbon, Budapest, Thessaloniki, Amsterdam, Florence; non-qualifying on type: Greek standards, EU data-sharing | datasets/qualifying_events_trailing_24m.csv; datasets/regulatory_factor_register_32.csv | 2026-09-05 | 2026-09-17 | yes |
| 5 | Register probabilities (team's own, single-analyst, no external calibration) for the loss-bearing outcome to be in force by end-2027: EU-AHA 0.12, ES-REMOVE 0.35, ES-REGIONS 0.45, PARIS-PRO 0.30, IT-NAT 0.30, GR-FREEZE 0.70, UK-ENG 0.20, IE-REG 0.35, PT-RETIGHT 0.20, NL-AMS 0.30, BCN-2028 0.00 | data/processed/abnb_regulatory_events.csv; research/notes/2026-09-05_regulatory-forecast-profile.md §2 | 2026-09-06 | 2026-09-17 | yes |
| 6 | EU Affordable Housing Act: proposal published 9 Sep 2026; enabling framework (housing-stress screen, price-to-income ≥ 8x, three-year adverse-effect proof, restrictions capped at five years renewable, primary residences exempt); "still requires approval from EU member states and the European Parliament"; ordinary legislative procedure median about 18 months (STR data regulation took 17 months) | sources/web_fetch_notes_2026-09-17.md (Skift 2026-09-09; EESC); data/processed/abnb_regulatory_events.csv EU-AHA base_rate | 2026-09-09 | 2026-09-17 | yes |
| 7 | Greece: the Athens districts 1-3 freeze runs to 31 Dec 2026; Law 5313/2026 lets a joint ministerial decision extend it; "no official 2027 extension decision ... has been published" (13 Aug 2026); 2026 is "a test year"; Thessaloniki first municipal community frozen from 1 Mar 2026 | sources/web_fetch_notes_2026-09-17.md (GTP 2026-01-26; thehostdaily 2026-08-13) | 2026-08-13 | 2026-09-17 | yes |
| 8 | Spain: the Supreme Court annulled the national single registry (judgment May 2026, published 8 Jun 2026); registration is regional; no replacement national platform-verification law found; the EU data-sharing regulation (applies since 20 May 2026) lowers the cost of a redesign | sources/web_fetch_notes_2026-09-17.md; data/processed/abnb_regulatory_events.csv ES-REMOVE gates | 2026-09-17 | 2026-09-17 | yes |
| 9 | Ireland's register launches 1 Dec 2026 with registration required by 31 Dec 2026 (delayed once from May 2026); Ireland ≈ 0.7% of EMEA nights, so it fails the gate on convention 4 | sources/web_fetch_notes_2026-09-17.md (gov.ie); claim 2 | 2026-09-17 | 2026-09-17 | yes |
| 10 | Paris: the Le Meur law gives the city quota powers over non-primary-residence rentals; the Council of State upheld Paris' commercial-space rule (15 Jul 2026); no quota vote found as of 17 Sep 2026 | sources/web_fetch_notes_2026-09-17.md; data/processed/abnb_regulatory_events.csv PARIS-PRO gates | 2026-09-17 | 2026-09-17 | no |
| 11 | England's registration scheme is not live after three slipped dates; UK digital-registration launches slip a median of 12+ months | data/processed/abnb_regulatory_events.csv UK-ENG | 2026-09-06 | 2026-09-17 | no |
| 12 | 0 of 41 ABNB moves ≥ 7% (2020-2026) were regulatory (drivers: macro 20, earnings 11, company 9, competitor 1); the catalyst calendar expects "low-single-digit unless a hard cap number appears" for the EU act | data/processed/abnb_big_moves_7pct.csv; research/notes/catalyst_calendar.md | 2026-09-05 | 2026-09-17 | yes (impact) |
| 13 | Register conditional losses for the events that can enact inside the window: ES-REMOVE 0.10/0.20/0.45% of revenue, PARIS-PRO 0.10/0.20/0.35, ES-REGIONS 0.05/0.15/0.35, IT-NAT 0.05/0.12/0.30, GR-FREEZE 0.02/0.05/0.12, UK-ENG 0.03/0.08/0.20; 2027 median regulatory drag 0.45% of revenue, $2.78/share at 22x | data/processed/abnb_regulatory_events.csv; abnb_regulatory_profile.csv | 2026-09-06 | 2026-09-17 | yes (impact) |
| 14 | No prediction market exists on European STR regulation (Polymarket public-search "short-term rental": irrelevant results only; the 5 Sep 2026 note found none on Kalshi or Metaculus) | sources/polymarket_search_short-term_rental_20260917T082126Z.json; research/notes/2026-09-05_regulatory-forecast-profile.md §3 | 2026-09-17 | 2026-09-17 | no |
| 15 | Final 72-hour check: nothing enacted since the 9 Sep proposal; no Greek decision, no Spanish replacement law, no Paris vote reported | sources/web_fetch_notes_2026-09-17.md (queries 1-3) | 2026-09-17 | 2026-09-17 | no |

## 2. Query Log
1. [repo] data/processed/abnb_regulatory_events.csv, abnb_regulatory_profile.csv, abnb_regulatory_contributions.csv (full dump)
2. [repo] data/processed/abnb_regulatory.sqlite: factors (32 rows), regulatory_market_inventory, regulatory_factor_exposure
3. [repo] research/notes/2026-09-05_regulatory-forecast-profile.md (§0-§5)
4. [repo] data/processed/overnight/10_regional_panel_quarterly.csv (EMEA nights share); data/processed/eurostat_platform_nights_by_country.csv; research/notes/2026-09-05_eu-platform-and-backlog.md
5. [repo] research/notes/catalyst_calendar.md (EU act row); data/processed/abnb_big_moves_7pct.csv driver counts
6. [repo] data/raw/regulatory/quantification listing (city files, 10-K/10-Q); abnb_2026q2_10q.html regional revenue table
7. [Polymarket API] public-search?q=short-term%20rental (2026-09-17T08:21:26Z)
8. WebSearch: EU Affordable Housing Act short-term rentals proposal September 2026
9. WebFetch: skift.com/2026/09/09/eu-proposed-rules-short-term-rentals/
10. WebSearch: Spain short-term rental registry replacement law 2026 Paris professional rentals quota vote
11. WebSearch: Greece Athens short-term rental registration freeze extension 2027 decision Ireland short-term letting register December 2026 launch
12. WebFetch: news.gtp.gr 2026-01-26 Greece restrictions article
13. WebFetch: thehostdaily.com/athens-airbnb-rules-2026-2027/ (2026-08-13)
14. [computed] datasets/qualifying_events_trailing_24m.csv; datasets/eurostat_country_shares_scaled_to_emea.csv

## 3. Leading Hypothesis Entities
European Commission, Affordable Housing Act, Spain, Paris, Le Meur law, Greece, Athens, Canary Islands, Italy, England registration scheme, Ireland register, Airbnb EMEA

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| EU Affordable Housing Act adopted with binding caps by 11 Feb 2027 | kept as tail (0.01) | Proposal 9 Sep 2026; no contested EU file has been adopted inside 15 months; the draft is enabling, not binding (claim 6) |
| Greek joint ministerial decision extends the Athens/Thessaloniki freeze into 2027 (by 31 Dec 2026) | kept but gated (0.60 that it is published in the window × 0.30 that it adds a ≥1% area or the resolver reads the national instrument as qualifying = 0.18) | Register 0.70 for the extension; Athens alone ≈ 0.5% of EMEA (claim 3); convention 4 |
| Spain enacts a replacement national registry with platform verification and removal | kept (0.15 inside the window) | Register 0.35 by end-2027; the annulment was on competence grounds and a redesign needs a law (claim 8) |
| Spanish regional measures (Andalusia, Valencia, Balearics enforcement law, Catalan decree renewals, Canary phased implementation steps) | kept (0.30) | Register ES-REGIONS 0.45 by end-2027; Spain has run three enforcement waves in 24 months; Canaries and Spain-wide regional instruments clear the gate |
| Paris council uses Le Meur powers (quota or ban on professional rentals) | kept (0.12) | Register 0.30 by end-2027; new council since March 2026; no vote scheduled (claim 10) |
| Italy national or art-city caps (Rome, Venice, Milan) | kept (0.12) | Register 0.30 by end-2027; one national measure a year since 2023 |
| England registration commencement regulations laid | kept (0.10) | Register 0.20; three slipped dates (claim 11) |
| Germany, Austria, Poland, Croatia, UK/London or another ≥1% market enacts a cap or moratorium not in the register | kept (0.10) | The register covers 32 factors but not every EU capital; the trailing-24-month count contains events the register did not pre-list (Budapest, Malaga) |
| Portugal re-tightens nationally | kept (0.05) | Register 0.20 by end-2027; policy reversed toward liberalisation in 2024 |
| Ireland register launch (1 Dec 2026) counts | discarded on the gate (0.7% of EMEA) | claim 9; priced as resolver leniency in section 7 |
| Barcelona licence withdrawal | discarded | November 2028; outside the effective-date gate |
| Amsterdam citywide 15-night cap, Lisbon removals, Madrid, Athens-only | discarded on the gate | claim 3 sizes; priced under "strict/lenient gate" in section 7 |

## 5. Independent Estimates
- base_rate_estimate: 0.70 — trailing 24 months (Sep 2024-Sep 2026) contain 6 qualifying enactments under conventions 1-4 (4 clear + 2 marginal, claim 4); window length 17 Sep 2026-11 Feb 2027 = 147 days = 4.8 months; λ = 6 × 4.8/24 = 1.2; P(≥1) = 1 − e^−1.2 = 0.70. Strict count (4 clear only): λ = 0.8, P = 0.55. Lenient count (adding the seven sub-1% city measures): λ = 2.6, P = 0.93
- decomposition_estimate: 0.73 — 1 − (1−0.18 Greece gated)(1−0.15 Spain national)(1−0.30 Spain regional)(1−0.12 Paris)(1−0.12 Italy)(1−0.10 England)(1−0.05 Portugal)(1−0.10 other ≥1% market)(1−0.01 EU act) = 1 − 0.273 = 0.73; the named pipeline is treated as independent draws, which overstates joint probability slightly (shared "European housing politics" factor, register rho 0.45), so read it as ≈ 0.70
- anchor_estimate: none — no market (claim 14); the register's per-event probabilities are the team's own and are already inside the decomposition
- anchor_value: n/a (NO_EXTERNAL_ANCHOR)
- final_estimate: 0.68 (credible interval 0.50–0.82)
- final_minus_anchor: n/a. The base rate and decomposition agree within 3 points from different constructions (a count of past enactments vs a forward pipeline); the width of the interval is the convention risk in section 7, not sampling noise

## 6. Final Numbers
P(Yes) = 0.68; credible interval 0.50–0.82.
Extreme-probability gate: not triggered.
Coherence: B05 is independent of the 5 Nov print questions; it correlates with nothing in X01 except through the stock path (S02/S03) at low-single-digit magnitude.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Convention 1 (any binding supply restriction counts; the title's examples are illustrative) | If the resolver requires a measure of the exemplified magnitude (licence withdrawal, national registry with removals, EU caps): 0.40 (Spain national 0.15 + Spain regional mass removals 0.15 + Paris ban 0.08 + other 0.08) |
| Convention 4 (Athens-only, Ireland, Amsterdam, Lisbon, Madrid fail the gate) | If the resolver accepts national instruments regardless of the affected city (Greek extension, Irish register): 0.85 |
| Convention 3 (a freeze extension counts as enacted anew) | If extensions do not count: 0.62 |
| Greek decision published in the window (0.60) | If the ministry lets the freeze lapse or decides after 11 Feb: −0.06 under the lenient gate, no change under the strict gate |
| Spain enacts a replacement registry law inside the window (0.15) | If a bill is tabled by November: 0.30 → final 0.74 |
| Correlation across European events (treated as independent) | With rho 0.45 the joint complement rises about 0.03: final 0.65 |

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-17 to 2026-10-31 | Council working-party and Parliament committee referrals on the Affordable Housing Act | Information only; the act cannot resolve this question |
| 2026-10-01 to 2026-11-30 | Spanish Council of Ministers agenda (replacement registry / platform law); Andalusia, Valencia and Balearic decrees; Catalan licence-renewal decisions | Any national bill approved by the Council of Ministers: +0.06; a regional decree with removals or a moratorium in a ≥1% region (Canaries, Andalusia, Balearics borderline): resolves Yes |
| 2026-11-05 | ABNB 3Q26 call | Management language on Spain/EU only; no probability change |
| 2026-12-01 | Ireland register launch | No change (fails the gate); note for the audit |
| 2026-12-15 to 2026-12-31 | Greek joint ministerial decision on the 2027 freeze | Published with an added area or national scope: resolves Yes under conventions 3-4; Athens/Thessaloniki only: +0.05 (resolver leniency) |
| 2027-01-15 | Paris council session calendar; Italian budget-law and regional STR measures | A scheduled Paris quota vote: +0.08 |
| 2027-01-31 | Hazard checkpoint: if nothing has enacted, the remaining window is 11 days | Snap to 0.15 unless a decision is scheduled inside the window |
| 2027-02-11 | Resolution | Apply conventions 1-4; record which measure resolved it |

## 9. Impact
If B05 resolves Yes, the modal event is a mid-sized enactment (Spanish regional or national registry step, Greek extension, an Italian or Parisian measure) with the register's conditional loss mode ≈ 0.10-0.20% of global revenue in run-rate, most of it landing after 30 Jun 2027 (claim 13). Deltas versus the memo's base case:

| Item | Delta if B05 happens | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | 0.0 | already printed by resolution |
| 4Q26 nights (pts) | **−0.05** | enactment-to-removal lag; at most a few weeks of effect inside Q4 |
| ADR (pts) | +0.0 to +0.1 | removed supply is lower-ADR urban stock; ignored |
| 4Q26 revenue ($M) | **−2** | 0.05pt × $30M |
| FY27 revenue ($M) | **−25** (0.15% of ~$15.6bn, half-year weighting on the run-rate mode) | claim 13; register profile |
| FY26 adj. EBITDA margin (pp) | 0.0 | |
| FY27 adj. EBITDA margin (pp) | **−0.10** (0.66 × 0.16pt of growth) | brief sensitivity |
| FY27 EPS ($) | **−0.02** ($25M × 0.66 × $0.0014) | brief sensitivity |
| Stock ($/share) | **−2.5** = −$0.7 fundamental (0.15pt of FY27 nights × $4.90) plus a −1% headline drift (regulatory headlines have never produced a ≥7% move, 0 of 41; the 9 Sep proposal is the template) | claim 12; brief sensitivity |
| **EV = P × impact** | **0.68 × −$2.5 = −$1.7/share**; the large-event tail (Spanish mass removal ≥ 25k ads or a Paris professional ban, P ≈ 0.20 inside the window) is −$5/share on its own (0.20 × −$5 = −$1.0 of the EV) | |
| Materiality | **Material by the letter of the $1/share rule, but only because the event is likely, not because it is large.** The memo should carry one line: "a European restriction is more likely than not to be enacted before February (~0.7), worth about 0.1-0.2% of revenue; no regulatory headline has ever moved the stock 7%." Quote the tail (Spain, Paris) as the version that matters | |

## RESUME
The next agent (audit response) should attack: (1) the ×0.8 EU27-to-EMEA scaling and the city anchors behind convention 4 (Paris 2.5%, London 2%, Rome 1.5%, Athens 0.5%), which decide whether the Greek extension and the Irish register count; a better estimate from the team's Inside Airbnb store (nights-weighted) would settle it; (2) the trailing-24-month count in `datasets/qualifying_events_trailing_24m.csv` (the two marginal rows change the base rate from 0.55 to 0.70); (3) the independence assumption in the pipeline product. Re-check the Greek ministry and the Spanish Council of Ministers agenda before quoting.
