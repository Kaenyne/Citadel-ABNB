# RESEARCH LOG

Revision 2 (2026-09-17, audit response to A15, Fable). Revision 1 (2026-09-17, initial forecast, Fable). Batch A15 (B04, B05, B06, B07). Reproduction: the base rate is a Poisson count from `datasets/qualifying_events_trailing_24m_v2.csv` with the window profile in `datasets/recency_profile_v2.csv` (revision-1 files untouched); the decomposition is the product in section 5; the market-size gate is `datasets/eurostat_country_shares_scaled_to_emea.csv` plus the city anchors in claim 3; the audit's `docs/pitch-forecasts/audits/A15-reproduce.py` replays every count and product.

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
- revision: 2
- revised: 2026-09-17
- agent: fable
- batch: A15
- audit: `docs/pitch-forecasts/audits/A15-research-audit.md` (independent Opus auditor standing in for Codex); response `docs/pitch-forecasts/audits/A15-audit-response.md`

## 0b. Question (verbatim)
### Title
By 11 Feb 2027, will a new short-term-rental restriction take effect or be enacted in an EU/UK city or country whose Airbnb nights exceed 1% of EMEA nights (e.g., a Barcelona-style licence withdrawal, a national registration regime with removal of unregistered listings, or the EU Affordable Housing Act with binding STR caps)?
### Resolution Criteria
**Type.** Binary. **Resolution.** Yes if enacted (not proposed) with an effective date on or before 30 Jun 2027 and the affected market ≥1% of EMEA nights by the team's regional panel. Resolution 11 Feb 2027.
### Fine Print
None beyond the resolution sentence. Conventions adopted (each priced in section 5 and section 7):
1. "Short-term-rental restriction" = a binding rule that reduces permitted STR supply or activity: a cap on nights, a ban or zone ban, a moratorium on new licences or registrations, a licence non-renewal, a registration regime whose enforcement removes non-compliant listings, or a principal-residence requirement. Tax changes, business-classification and threshold rules (the Italian cedolare and budget-law thresholds), data-sharing rules, safety/operating standards and platform fines alone do not count. The "e.g." list in the title is illustrative, not a magnitude floor.
2. "Enacted" = adopted by the competent body (statute, decree, council vote, joint ministerial decision, commencement regulations), not proposed, drafted or announced. The measure must be enacted between 17 Sep 2026 and 11 Feb 2027, **or** be a measure enacted before 17 Sep 2026 whose commencement date falls inside the window ("take effect", as the title says). The take-effect route is operationalised in claim 16: every already-enacted measure in the register and the 32-factor inventory with a dated commencement was checked; none in a ≥1% market commences inside the window, so the route is priced as a residual for an undated implementing step (Canary municipal rules, a Spanish regional commencement on 1 Jan 2027), not as a named event.
3. An extension of an expiring freeze by a new decision counts as newly enacted (it is a fresh act of the competent body that restricts supply for a new period).
4. Market size: the team's regional panel gives EMEA ≈ 40% of nights but no city shares; the gate is applied with the team's exposure anchors, which are **GBV and revenue shares, not nights shares**: national measures qualify in FR, ES, IT, DE, EL (Greece), PT, PL, HR, AT and the UK (each ≥ 2% of EMEA); Paris (~2.5% of EMEA GBV, ~1.7% of EMEA nights at a 1.45x city ADR premium), London (~2% GBV, ~1.4% nights), the Canary Islands (~2.2%) qualify; Rome (~1.5% GBV, ~1.05% nights) is **on the line**; Barcelona (~0.5%), Madrid (~0.7%), Lisbon (~0.55%), Athens (~0.5%), Amsterdam (~0.35%), Florence (~0.4%), Ireland (~0.7%), the Netherlands (~1.0%, borderline) and the Balearics (~1.0%, borderline) do not qualify on a city/region-only measure. A national instrument that restricts only one sub-1% city (the Greek Athens/Thessaloniki freeze) is treated as failing the gate; the alternative reading is priced in section 7. Nothing in the decomposition turns on Rome: the Italy route is a national measure and Italy is 11.7% of EMEA.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Airbnb EMEA nights share estimate 39.6-40.0% of global nights (2Q26); EMEA revenue 40% of 2Q26 revenue ($1,425M of $3,608M); the regional GBV/nights conversion is ~1:1 (39.6 vs 39.5), the within-region city conversion is not | data/processed/overnight/10_regional_panel_quarterly.csv (emea_nights_share_est_pct, emea_revenue_share_pct); data/raw/regulatory/quantification/abnb_2026q2_10q.html | 2026-08-06 | 2026-09-17 | yes |
| 2 | Eurostat **four-platform** nights (Airbnb, Booking, Expedia, TripAdvisor) 2025 shares of EU27: FR 22.3%, ES 19.9%, IT 14.6%, DE 7.2%, EL 5.5%, PT 5.2%, PL 4.7%, HR 4.4%, AT 2.6%, BE 1.4%, HU 1.4%, CZ 1.3%, NL 1.25%, IE 0.9%; scaled by 0.8 (EU27 ≈ 80% of EMEA, the rest UK, CH, NO, Turkey, Middle East, Africa) to EMEA shares. **Cross-check of the scaler:** the register's ES-REMOVE anchor derives Spain ≈ 6% of global revenue (20% of EU platform nights × ~30% EU share of revenue), i.e. ~15% of EMEA, against the scaled table's 15.93%. Platform-mix bias (France Airbnb-heavy; Croatia, Greece, Italy Booking-heavy) means the borderline rows (AT 2.09%, NL 1.00%) are not reliable to the second decimal | data/processed/eurostat_platform_nights_by_country.csv; datasets/eurostat_country_shares_scaled_to_emea.csv; data/processed/abnb_regulatory_events.csv (ES-REMOVE anchor) | 2026-09-05 | 2026-09-17 | yes |
| 3 | Team exposure anchors (GBV/revenue basis): Paris ≈ 1.0% of global GBV, London ≈ 0.8%, Rome ≈ 0.6%, Ireland ≈ 0.4% of global revenue, Spain ≈ 6% of global revenue, Netherlands 1.3% and Portugal 5.2% of EU platform nights; Canary Islands 48,356 of Spain's 341,001 INE tourist dwellings (14.2%), Balearics 21,304 (6.2%); Inside Airbnb June 2026 listing counts Paris 77,679, London 92,799, Madrid 22,835, Lisbon 17,098, Barcelona 15,406, Athens 14,342, Florence 13,508, Amsterdam 10,465 | data/processed/abnb_regulatory_events.csv (anchor column); datasets/regulatory_market_inventory.csv | 2026-09-06 | 2026-09-17 | yes |
| 4 | Qualifying enacted measures in the trailing 24 months under conventions 1-4: Paris 90-night cap (Le Meur law, enacted Nov 2024, effective 1 Jan 2025); Spain Horizontal Property Law neighbour-approval rule (3 Apr 2025); Spain national registry plus the 65,935-ad removal order (May-Jul 2025); Canary Islands Law 6/2025 (10 Dec 2025); plus two marginal: Italy CIN mandatory (Jan 2025; registration without removal) and the Greek Athens freeze (national law, Jan 2025; Athens alone < 1%). **All six are dated Nov 2024 – Dec 2025; none of the 2026 rows qualifies**: Budapest, Thessaloniki, Amsterdam, Florence fail the gate; the EU data-sharing regulation and the Italian 2026 budget-law business-threshold change (register IT-NAT gates; added at revision 2) fail on type. Non-qualifying on the gate: Malaga, Madrid, Lisbon. Recency profile: trailing 12 months 1 event, 18 months 3, 24 months 6; 4 policy clusters in 24 months (Spain's three 2025 measures are one enforcement wave) | datasets/qualifying_events_trailing_24m_v2.csv; datasets/recency_profile_v2.csv; datasets/regulatory_factor_register_32.csv | 2026-09-05 | 2026-09-17 | yes |
| 5 | Register probabilities (team's own, single-analyst, no external calibration) for the **loss-bearing outcome** to be in force by end-2027 (a 15.5-month horizon and a harder event than enactment: ES-REMOVE "at least 25,000 more ads offline", ES-REGIONS "remove or freeze a measurable share", IE-REG "removes more than 20%", UK-ENG "remove or cap supply in at least two large tourist areas", IT-NAT "night caps or zone bans in Rome, Venice, Milan", PARIS-PRO "quota or ban"): EU-AHA 0.12, ES-REMOVE 0.35, ES-REGIONS 0.45, PARIS-PRO 0.30, IT-NAT 0.30, GR-FREEZE 0.70, UK-ENG 0.20, IE-REG 0.35, PT-RETIGHT 0.20, NL-AMS 0.30, BCN-2028 0.00 | data/processed/abnb_regulatory_events.csv; research/notes/2026-09-05_regulatory-forecast-profile.md §2 | 2026-09-06 | 2026-09-17 | yes |
| 6 | EU Affordable Housing Act: proposal published 9 Sep 2026; enabling framework (housing-stress screen, price-to-income ≥ 8x, three-year adverse-effect proof, restrictions capped at five years renewable, primary residences exempt); "still requires approval from EU member states and the European Parliament"; ordinary legislative procedure median about 18 months (STR data regulation took 17 months) | sources/web_fetch_notes_2026-09-17.md (Skift 2026-09-09; EESC); data/processed/abnb_regulatory_events.csv EU-AHA base_rate | 2026-09-09 | 2026-09-17 | yes |
| 7 | Greece: the Athens districts 1-3 freeze runs to 31 Dec 2026; Law 5313/2026 lets a joint ministerial decision extend it; "no official 2027 extension decision ... has been published" (13 Aug 2026); 2026 is "a test year"; Thessaloniki first municipal community frozen from 1 Mar 2026 (GTP) / 1 Jul 2026 (register REG-05) | sources/web_fetch_notes_2026-09-17.md (GTP 2026-01-26; thehostdaily 2026-08-13) | 2026-08-13 | 2026-09-17 | yes |
| 8 | Spain: the Supreme Court annulled the national single registry (judgment May 2026, published 8 Jun 2026); registration is regional; no replacement national platform-verification law found; the EU data-sharing regulation (applies since 20 May 2026) lowers the cost of a redesign | sources/web_fetch_notes_2026-09-17.md; data/processed/abnb_regulatory_events.csv ES-REMOVE gates | 2026-09-17 | 2026-09-17 | yes |
| 9 | Ireland's register launches 1 Dec 2026 with registration required by 31 Dec 2026 (delayed once from May 2026); Ireland ≈ 0.7% of EMEA nights, so it fails the gate on convention 4; it is also a registration without removal until enforcement | sources/web_fetch_notes_2026-09-17.md (gov.ie); claim 2 | 2026-09-17 | 2026-09-17 | yes |
| 10 | Paris: the Le Meur law gives the city quota powers over non-primary-residence rentals; the Council of State upheld Paris' commercial-space rule (15 Jul 2026); no quota vote found as of 17 Sep 2026 | sources/web_fetch_notes_2026-09-17.md; data/processed/abnb_regulatory_events.csv PARIS-PRO gates | 2026-09-17 | 2026-09-17 | no |
| 11 | England's registration scheme is not live after three slipped dates; UK digital-registration launches slip a median of 12+ months | data/processed/abnb_regulatory_events.csv UK-ENG | 2026-09-06 | 2026-09-17 | no |
| 12 | 0 of 41 ABNB moves ≥ 7% (2020-2026) were regulatory (drivers: macro 20, earnings 11, company 9, competitor 1); the catalyst calendar expects "low-single-digit unless a hard cap number appears" for the EU act. **Around the EU proposal (Reuters draft report 4 Sep, presentation 9 Sep 2026) ABNB closed −4.07% on 8 Sep and −2.81% on 9 Sep (QQQ −0.08% / −0.29%), −6.8% over the two days**, on days that also carried the Iran-Jordan missile strikes and the oil spike, so attribution is shared; below the 7% daily threshold of the big-moves file | data/processed/abnb_big_moves_7pct.csv; research/notes/catalyst_calendar.md; yfinance daily closes ABNB/QQQ 3-11 Sep 2026 (retrieved 2026-09-17) | 2026-09-11 | 2026-09-17 | yes (impact) |
| 13 | Register conditional losses for the events that can enact inside the window: ES-REMOVE 0.10/0.20/0.45% of revenue, PARIS-PRO 0.10/0.20/0.35, ES-REGIONS 0.05/0.15/0.35, IT-NAT 0.05/0.12/0.30, GR-FREEZE 0.02/0.05/0.12, UK-ENG 0.03/0.08/0.20; 2027 median regulatory drag 0.4499% of revenue, $2.78/share at 22x | data/processed/abnb_regulatory_events.csv; abnb_regulatory_profile.csv | 2026-09-06 | 2026-09-17 | yes (impact) |
| 14 | No prediction market exists on European STR regulation (Polymarket public-search "short-term rental": irrelevant results only; the 5 Sep 2026 note found none on Kalshi or Metaculus) | sources/polymarket_search_short-term_rental_20260917T082126Z.json; research/notes/2026-09-05_regulatory-forecast-profile.md §3 | 2026-09-17 | 2026-09-17 | no |
| 15 | Final 72-hour check: no enactment since the 9 Sep proposal, no Greek decision, no Spanish replacement law and no Paris vote **in the searches and fetches recorded** | sources/web_fetch_notes_2026-09-17.md (queries 1-3) | 2026-09-17 | 2026-09-17 | no |
| 16 | Take-effect enumeration (convention 2): already-enacted measures with dated commencements: Ireland register 1 Dec 2026 (fails gate); Greek Athens freeze **expires** 31 Dec 2026 (an expiry is not a commencement; an extension is a new act, priced as the Greece route); Thessaloniki freeze runs to 31 Dec 2026; Canary Law 6/2025 "phased implementation", no dated municipal step found; Florence expansion effective 21 Jun 2026 (past; sub-1%); Amsterdam evaluation due 2027; Malaga moratorium to Aug 2028; Barcelona Nov 2028; Maui/NYC outside EMEA. **No enacted measure in a ≥1% market commences inside 17 Sep 2026 – 11 Feb 2027** | datasets/regulatory_factor_register_32.csv (dates, next_catalyst); data/processed/abnb_regulatory_events.csv (gates) | 2026-09-06 | 2026-09-17 | yes |

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
15. [rev 2, repo] data/processed/abnb_regulatory_events.csv full row dump (event, gates, dates, anchor for every id) to read the register's event bars and the IT-NAT budget-law gate
16. [rev 2, repo] datasets/regulatory_factor_register_32.csv `dates` and `next_catalyst` columns for every factor, to enumerate commencements inside the window (claim 16)
17. [rev 2, computed] datasets/qualifying_events_trailing_24m_v2.csv (adds the Italian budget-law row) and datasets/recency_profile_v2.csv (12/18/24-month and cluster counts)
18. [rev 2, yfinance] ABNB and QQQ daily closes 3-11 Sep 2026 for the proposal-window reaction (claim 12)
19. [rev 2, repo] docs/pitch-forecasts/audits/A15-reproduce.py run from the repo root (`py -3.13 -B`), output in `A15-reproduce.stdout.txt`

## 3. Leading Hypothesis Entities
European Commission, Affordable Housing Act, Spain, Paris, Le Meur law, Greece, Athens, Canary Islands, Italy, England registration scheme, Ireland register, Airbnb EMEA

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| EU Affordable Housing Act adopted with binding caps by 11 Feb 2027 | kept as tail (0.01) | Proposal 9 Sep 2026; no contested EU file has been adopted inside 15 months; the draft is enabling, not binding (claim 6) |
| Greek joint ministerial decision extends the Athens/Thessaloniki freeze into 2027 (by 31 Dec 2026) | kept but gated (0.60 that it is published in the window × 0.30 that it adds a ≥1% area or the resolver reads the national instrument as qualifying = 0.18); the decision date is inside the window, so no window scaling applies | Register 0.70 for the extension; Athens alone ≈ 0.5% of EMEA (claim 3); convention 4 |
| Spain enacts a replacement national registry with platform verification and removal | kept (0.12 inside the window; register 0.35 × window 0.31 = 0.11, bar relaxed from "25,000 more ads offline" to "law enacted" ×1.1) | The annulment was on competence grounds and a redesign needs a law (claim 8); no bill tabled as of 17 Sep |
| Spanish regional measures (Andalusia, Valencia, Balearics enforcement law, Catalan decree renewals, Canary implementing rules) | kept (0.30; register 0.45 × 0.31 = 0.14, bar relaxed from "measurable share removed or frozen" to "any enacted regional decree or moratorium in a ≥1% region" ×2) | Spain has run three enforcement waves in 24 months; Canaries and Spain-wide regional instruments clear the gate |
| Paris council uses Le Meur powers (quota or ban on professional rentals) | kept (0.10; 0.30 × 0.31 = 0.09, ×1.1 for enactment vs in force) | New council since March 2026; no vote scheduled (claim 10) |
| Italy national or art-city caps (Rome, Venice, Milan), including a STR-restricting provision in the 2027 budget law (enacted late December, commencing 1 January) | kept (0.12; 0.30 × 0.31 = 0.09, ×1.3 because a cap enacted but not yet in force counts here) | One national measure a year since 2023, but the 2026 precedent was a threshold rule that fails convention 1 on type; a budget-law provision must be a cap or ban to count |
| England registration commencement regulations laid | kept (0.07; 0.20 × 0.31 = 0.06, ×1.1) | Three slipped dates (claim 11) |
| Germany, Austria, Poland, Croatia, UK/London or another ≥1% market enacts a cap or moratorium not in the register | kept (0.10) | The register covers 32 factors but not every EU capital; the trailing-24-month count contains events the register did not pre-list (Budapest, Malaga) |
| Portugal re-tightens nationally | kept (0.04; 0.20 × 0.31 = 0.06, ×0.7 because policy is liberalising and a reversal needs a new government act) | Register 0.20 by end-2027; policy reversed toward liberalisation in 2024 |
| An already-enacted measure takes effect inside the window (convention 2) | kept as a residual (0.08) after enumeration found no dated commencement in a ≥1% market (claim 16) | Canary municipal implementing steps and 1 January regional commencements are the candidates; none is dated |
| Ireland register launch (1 Dec 2026) counts | discarded on the gate (0.7% of EMEA) | claim 9; priced as resolver leniency in section 7 |
| Barcelona licence withdrawal | discarded | November 2028; outside the effective-date gate |
| Amsterdam citywide 15-night cap, Lisbon removals, Madrid, Athens-only | discarded on the gate | claim 3 sizes; priced under "strict/lenient gate" in section 7 |

## 5. Independent Estimates
- base_rate_estimate: 0.50 — a Poisson rate on the trailing count is not stationary (claim 4): all six qualifying enactments fall in Nov 2024 – Dec 2025 and none in the 8.5 months since, while 2026's activity has been in sub-1% cities. Window 17 Sep 2026 – 11 Feb 2027 = 147 days = 4.83 months. Profile (`recency_profile_v2.csv`): trailing 24 months 6 events → λ 1.21, P(≥1) = 0.70 (revision 1); trailing 18 months 3 → λ 0.80, 0.55; trailing 12 months 1 → λ 0.40, 0.33; 4 policy clusters in 24 months → 0.55. Strict count (4 clear only, 24 months) 0.55; lenient (adding the seven sub-1% city measures) 0.93. The base-rate leg is taken at **0.50**, the 18-month/cluster value discounted a little for the silent 2026, with 0.33–0.70 as the bracket
- decomposition_estimate: 0.67 — routes (section 4, each shown as register p27 × window 4.83/15.5 = 0.31 × a bar adjustment from the register's loss-bearing outcome to bare enactment, or a direct judgement where no register row exists): 1 − (1−0.18 Greece gated)(1−0.12 Spain national)(1−0.30 Spain regional)(1−0.10 Paris)(1−0.12 Italy)(1−0.07 England)(1−0.04 Portugal)(1−0.10 other ≥1% market)(1−0.01 EU act)(1−0.08 take-effect residual) = 1 − 0.293 = **0.707** (0.68 without the take-effect route). The named pipeline is treated as independent draws, which overstates the joint probability (shared "European housing politics" factor, register rho 0.45), so read it as ≈ **0.67**
- anchor_estimate: none — no market (claim 14); the register's per-event probabilities are the team's own and are already inside the decomposition
- anchor_value: n/a (NO_EXTERNAL_ANCHOR)
- final_estimate: 0.62 (credible interval 0.42–0.78)
- final_minus_anchor: n/a. The base rate (0.50) and decomposition (0.67) are 17 points apart because the count leg is dominated by a 2025 Spanish enforcement wave that has gone quiet and the pipeline leg prices the specific decisions due inside the window (the Greek decision by 31 Dec, the Spanish regional calendar, the Italian budget law); the final leans to the pipeline, which is the better-specified leg, and sits 6 points below revision 1's 0.68. Audit A15's independent 0.62 (pipeline 0.665 + take-effect 0.20 → 0.73, correlation → 0.67, blended with the 0.33–0.55 base leg) reproduces the same structure; this log prices the take-effect route at 0.08, not 0.20, because the enumeration in claim 16 found no dated in-window commencement, and lands on the same number

## 6. Final Numbers
P(Yes) = 0.62; credible interval 0.42–0.78.
Extreme-probability gate: not triggered.
Coherence: B05 is independent of the 5 Nov print questions; it correlates with nothing in X01 except through the stock path (S02/S03) at low-single-digit magnitude.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Convention 1 (any binding supply restriction counts; the title's examples are illustrative) | If the resolver requires a measure of the exemplified magnitude (licence withdrawal, national registry with removals, EU caps): 0.38 (Spain national 0.12 + Spain regional mass removals 0.15 + Paris ban 0.08 + other 0.08) |
| Convention 4 (Athens-only, Ireland, Amsterdam, Lisbon, Madrid fail the gate) | If the resolver accepts national instruments regardless of the affected city (Greek extension, Irish register): 0.80 |
| Convention 3 (a freeze extension counts as enacted anew) | If extensions do not count: 0.57 |
| Convention 2 take-effect route (0.08 residual) | If a dated Canary municipal implementing rule or a 1 Jan 2027 regional commencement surfaces: resolves Yes; if the resolver reads the title's "new" as excluding pre-enacted measures: 0.60 |
| Base-rate window | 24-month count (0.70) as the base leg: 0.66; 12-month count (0.33): 0.55 |
| Greek decision published in the window (0.60) | If the ministry lets the freeze lapse or decides after 11 Feb: −0.06 under the lenient gate, no change under the strict gate |
| Spain enacts a replacement registry law inside the window (0.12) | If a bill is tabled by November: 0.30 → final 0.68 |
| Correlation across European events (rho 0.45) | If treated as independent: 0.65 |

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-17 to 2026-10-31 | Council working-party and Parliament committee referrals on the Affordable Housing Act | Information only; the act cannot resolve this question |
| 2026-10-01 to 2026-11-30 | Spanish Council of Ministers agenda (replacement registry / platform law); Andalusia, Valencia and Balearic decrees; Catalan licence-renewal decisions; Canary municipal implementing rules | Any national bill approved by the Council of Ministers: +0.06; a regional decree with removals or a moratorium in a ≥1% region (Canaries, Andalusia, Balearics borderline): resolves Yes; a dated Canary implementing step inside the window: resolves Yes |
| 2026-11-05 | ABNB 3Q26 call | Management language on Spain/EU only; no probability change |
| 2026-12-01 | Ireland register launch | No change (fails the gate); note for the audit |
| 2026-12-15 to 2026-12-31 | Greek joint ministerial decision on the 2027 freeze; Italian 2027 budget law (STR provisions) | Greek decision with an added area or national scope: resolves Yes under conventions 3-4; Athens/Thessaloniki only: +0.05 (resolver leniency); an Italian budget-law cap or zone ban: resolves Yes; a tax/threshold change only: no change |
| 2027-01-15 | Paris council session calendar; Italian regional STR measures | A scheduled Paris quota vote: +0.08 |
| 2027-01-31 | Hazard checkpoint: if nothing has enacted, the remaining window is 11 days | Snap to 0.12 unless a decision is scheduled inside the window |
| 2027-02-11 | Resolution | Apply conventions 1-4; record which measure resolved it |

## 9. Impact
If B05 resolves Yes, the modal event is a mid-sized enactment (Spanish regional or national registry step, Greek extension, an Italian or Parisian measure) with the register's conditional loss mode ≈ 0.10-0.20% of global revenue in run-rate, most of it landing after 30 Jun 2027 (claim 13). Deltas versus the memo's base case:

| Item | Delta if B05 happens | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | 0.0 | already printed by resolution |
| 4Q26 nights (pts) | **−0.05** | enactment-to-removal lag; at most a few weeks of effect inside Q4 |
| ADR (pts) | +0.0 to +0.1 | removed supply is lower-ADR urban stock; ignored |
| 4Q26 revenue ($M) | **−2** | 0.05pt × $30M |
| FY27 revenue ($M) | **−12** (0.15% of ~$15.6bn = $23M run-rate, half-year weighted because the mode lands after 30 Jun 2027) | claim 13; register profile |
| FY26 adj. EBITDA margin (pp) | 0.0 | |
| FY27 adj. EBITDA margin (pp) | **−0.05** (0.66 × 0.08pt of growth) | brief sensitivity |
| FY27 EPS ($) | **−0.01** ($12M × 0.66 × $0.0014) | brief sensitivity |
| Stock ($/share) | **−2.1** = −$0.4 fundamental (0.08pt of FY27 nights × $4.90) plus a −1% headline term (−$1.7 on $167.51; regulatory headlines have never produced a ≥7% daily move, 0 of 41, but the 8-9 Sep 2026 proposal window saw −6.8% against QQQ −0.4% with shared attribution, claim 12) | claim 12; brief sensitivity |
| **EV, level basis = P × impact** | **0.62 × −$2.1 = −$1.3/share**; the large-event tail (Spanish mass removal ≥ 25k ads or a Paris professional ban, P ≈ 0.20 inside the window) is −$5/share on its own (0.20 × −$5 = −$1.0 of the EV) | |
| **EV, surprise basis = (1 − P) × impact** | **0.38 × −$2.1 = −$0.8/share** — the memo trades the surprise, not the level: a 0.62-probability event is already mostly in the price | |
| Materiality | **Not material** on the surprise basis (under $1/share); material only by the letter of the level rule, and only because the event is likely, not because it is large. The memo should carry one line: "a European restriction is more likely than not to be enacted before February (~0.6), worth about 0.1-0.2% of revenue; no regulatory headline has ever moved the stock 7% in a day." Quote the tail (Spain, Paris) as the version that matters | |

## 10. Revision notes
| Change | Finding |
|---|---|
| Metadata: revision 2, revised 2026-09-17; audit and response paths added | — |
| Claim 4 and §5: the Poisson rate published as a recency profile (24m 0.70 / 18m 0.55 / 12m 0.33 / clusters 0.55, `recency_profile_v2.csv`); base-rate leg 0.70 → **0.50**; all six events dated Nov 2024 – Dec 2025 stated | A15-04 |
| §5: decomposition product corrected (rev 1 "1 − 0.273 = 0.73" was 0.712 on its own inputs); revision-2 routes give 0.707, read as 0.67 after the rho-0.45 correlation | A15-11 |
| §4: each register-derived route now shows the two adjustments separately (window 4.83/15.5 = 0.31; bar relaxation from the register's loss-bearing outcome to bare enactment, up for most routes, down for Portugal); Greece not window-scaled because the decision date is inside the window | A15-12 |
| Convention 2 operationalised: every already-enacted measure with a dated commencement enumerated (claim 16); none in a ≥1% market commences inside the window; take-effect route priced as a 0.08 residual (not the audit's +0.15–0.20) and carried in §7 | A15-13 |
| Claim 4 / `qualifying_events_trailing_24m_v2.csv`: Italian 2026 budget-law threshold row added with verdict "no (tax/business-classification rule)"; convention 1 now names tax and threshold rules as excluded; trailing-12-month count stays at 1 | A15-21 |
| §9: EV reported on both bases (level −$1.3, surprise −$0.8); **material flag off** on the surprise basis; the −1% headline term kept with the 8-9 Sep 2026 proposal-window reaction (−6.8% vs QQQ −0.4%, shared attribution) as its evidence | A15-14 |
| §9: FY27 revenue −25 → −12 (half-year weighting applied, as the description said); margin −0.10 → −0.05; EPS −0.02 → −0.01; stock −2.5 → −2.1 | A15-22 |
| Convention 4 and claim 3: gate stated as GBV/revenue-based; nights conversions given (Paris ~1.7%, London ~1.4%, Rome ~1.05% — on the line); nothing in the decomposition turns on Rome | A15-19 |
| Claim 2: Eurostat series labelled four-platform; the ×0.8 scaler cross-checked against the register's Spain anchor (15.9% vs ~15%); platform-mix caveat on AT/NL borderline rows | A15-20 |
| Claim 15: "in the searches and fetches recorded" | A15-25 |
| §7: base-rate-window and take-effect rows added; convention-1 strict 0.40 → 0.38, convention-4 lenient 0.85 → 0.80, extensions-excluded 0.62 → 0.57, Spain bill 0.74 → 0.68, independence 0.65; §8 Greek/Italian December row and Canary implementing steps added; hazard snap 0.15 → 0.12 | A15-04, A15-13 |
| Final 0.68 (0.50–0.82) → **0.62 (0.42–0.78)**; audit's independent 0.62 matched by a different take-effect weight (0.08 vs 0.20) and a higher base leg (0.50 vs 0.33–0.55) | A15-04, A15-11, A15-12, A15-13 |

## RESUME
The next agent should (1) re-check the Greek ministry, the Spanish Council of Ministers agenda, the Canary municipal implementing calendar and the Italian 2027 budget-law text before quoting — the Greek decision and the budget law are the two dated events inside the window; (2) keep the base-rate leg on the recency profile, not the 24-month count, unless a ≥1% enactment lands before November (which would restore the 24-month rate and take the final toward 0.70); (3) treat the −1% headline term as a judgement backed by one shared-attribution episode (8-9 Sep 2026), and drop it if the 5 Nov call shows the market ignoring the EU act. The audit's 0.62 and this log's 0.62 agree; the residual disagreement is only over how much of the pipeline is already-enacted measures taking effect (0.08 here, 0.20 there), which claim 16's enumeration settles unless a dated commencement surfaces.
