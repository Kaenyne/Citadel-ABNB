# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable). Batch A15 (B04, B05, B06, B07 share the web budget accounting; each log carries its own complete claims ledger and query log). No script is needed to reproduce the numbers: every computation is a one-line product or sum shown in section 5 and section 9.

## 0. Metadata
- question_name: bonus-host-churn-cited
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § B04)
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
By the Feb print, will management or the 10-K/10-Q attribute slower active-listing growth, host attrition, or lower host pricing competitiveness to the single-fee migration, or disclose active listings growth ≤ +3% y/y?
### Resolution Criteria
**Type.** Binary. **Resolution.** Yes on either. Resolution ~11 Feb 2027.
### Fine Print
None given in the registry. Conventions adopted (each priced as a resolver risk in section 5):
1. Leg 1 (attribution) requires a statement of an observed or expected effect that the company itself ties to the single-fee migration: e.g. "some hosts chose to leave the platform / paused listings after the fee change", "supply growth moderated as hosts adjusted to the single fee", "hosts raised prices to offset the fee, which made listings less competitive". A forward-looking risk-factor sentence ("the transition ... may cause some hosts to raise prices or discontinue hosting") in the 10-K/10-Q is hypothetical boilerplate and resolves No. A statement that hosts *absorbed* the fee (lower guest prices) is the opposite sign and resolves No.
2. Leg 2 (≤ +3%) requires a numeric or bucket disclosure that implies ≤3% ("low single digits", "approximately 3%", "flat"). The standing sentence "active listings grew relatively in line with Nights and Seats Booked" resolves No while nights grow above 3%. A level-only disclosure ("over 9 million") resolves No.
3. Window and documents: the 5 Nov 2026 letter, call and 3Q26 10-Q; the ~11 Feb 2027 letter and call; the FY26 10-K if filed by the Feb print or within the same week; conference appearances and 8-Ks between 17 Sep 2026 and the Feb print. Letter governs over call where they differ.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Active-listings growth was last disclosed as a percentage in 1Q24 (+15%; +17% ex quality removals); from 1Q25 every letter says supply grew "approximately in line with" or "slightly above" Nights and Seats Booked (i.e. 8-10%); 4Q25 "over 9 million"; the 2Q26 letter contains no active-listings sentence at all (0 hits), only "our supply strategy is deliberate and precise" and 150,000 World Cup listings | sources/letters_active_listings_supply_passages_4Q20-2Q26.txt; data/raw/letters/*.htm; docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md §4 | 2026-08-06 | 2026-09-17 | yes |
| 2 | Airbnb "has form for dropping metrics that stop flattering": 1BR-vs-hotel comparison ended after 4Q23, long-term-stay share and cross-border share after 1Q24, listings growth after 1Q24 | docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md §6 row 7 | 2026-09-11 | 2026-09-17 | yes |
| 3 | Management framing of the migration is uniformly positive on the record: 4Q25 call (Mertz, to Kopelman): "we obviously very diligently managed the communication with our hosts to ensure that they did not perceive this as a fee increase ... many of the hosts did not take up their rates. Instead, the effective ADR to guests came down modestly"; 1Q26 call: "will help our hosts price more competitively"; 2Q26 call: "helped our host price more competitively and provided greater price transparency. As a result of its success, we recently announced the broader rollout ... Approximately half of our active listings are now subject to the single service fee"; 2Q26 Chesky: "we haven't really gotten much feedback from our core hosts. Mostly, they just want to make sure their bookings are going up, and our results show they are" | sources/fee_migration_passages_4Q25-2Q26.txt; data/raw/transcripts/web/4Q25.html, 1Q26.html, 2Q26.html | 2026-08-06 | 2026-09-17 | yes |
| 4 | The FY25 10-K describes the single-fee transition neutrally in the revenue-recognition note ("In October 2025, the Company began transitioning to a single-fee structure, charging only the host a service fee") and lists "the service fees we charge" among host-competition factors; it contains no host-attrition risk sentence tied to the fee and no active-listings growth figure ("no single city ... more than 1% of our active listings") | data/raw/regulatory/quantification/abnb_2025_10k.json | 2026-02 | 2026-09-17 | yes |
| 5 | The 2Q26 10-Q carries no fee-migration host language beyond forward-looking-statement boilerplate ("our ability to attract and retain hosts and guests") | data/raw/regulatory/quantification/abnb_2026q2_10q.html | 2026-08-06 | 2026-09-17 | no |
| 6 | Team fee-churn panel: the October 2025 PMS migration produced no disappearance spike (11 markets: 4.10% Sep-Oct, 3.03% Oct-Nov, 3.43% Nov-Dec); the Dec-Jan 12.74% spike is a capture-composition artefact (zero previous-scrape rows; 65-90% of missing IDs reappear); 13-market Jun-Jul 3.63% and Jul-Aug 4.14% all-ID disappearance with longer intervals, "does not establish acceleration"; London (UK hosts migrated 22 Jun) 5.12% / 4.95% | research/notes/2026-09-07_fee-churn-catalyst.md; research/notes/2026-09-07_fee-churn-recent-followup.md; data/processed/fee_churn_recent/pooled_rates.csv | 2026-09-07 | 2026-09-17 | yes |
| 7 | Direct host-response evidence is anecdotal: one listing (31054261) steering guests to a competitor over the 15.5% fee; four Reddit accounts of final stays/deactivations (1 Sep 2026); explicit fee-related exit intentions (Jul 2026); none independently matched to a completed, fee-caused delisting | research/notes/2026-09-07_fee-churn-recent-followup.md table F01-F10 | 2026-09-07 | 2026-09-17 | no |
| 8 | Remaining hosts migrate by 15 Sep 2026 (non-EEA) and 13 Oct 2026 (EEA/CH); the team's migrated-share path is 62% of listings in 3Q26 and 94% in 4Q26; meaningful 90-day disappearance confirmation for Oct-Nov absences arrives "around January/February 2027 or later" | research/notes/2026-09-07_fee-churn-catalyst.md; data/processed/forecast_methods/fee_takerate/03_migrated_share_path.csv | 2026-09-07 | 2026-09-17 | yes |
| 9 | The 2019-2020 forced host-only migration (mandatory Dec 2020 outside the Americas) produced no published attrition or listing-count effect; Airbnb's only number was "+17% bookings" for hosts who "priced competitively" | research/notes/host_only_fee_history_and_elasticity.md §1 | 2026-09-06 | 2026-09-17 | yes |
| 10 | Nights per average active listing has been 62.5-62.7 for four years (2022-25), so listings growth co-moves with nights; a genuine collapse in listings growth would be visible in nights within quarters | docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md §2; data/processed/overnight/11_supply_economics.csv | 2026-09-11 | 2026-09-17 | yes |
| 11 | Morgan Stanley (Nowak, Underweight, PT $125, 30 Jul 2026) argues active-listings growth slowed from ~12% (2018-22) to ~7%; the debate is live on the Street, so an analyst question on supply is likely on both calls | research/notes/2026-09-04_abnb-pitch-catalogue.md (Morgan Stanley entry) | 2026-09-04 | 2026-09-17 | no |
| 12 | Management has declined to quantify supply detail repeatedly (2022Q2 listings ex-China, 2022Q4 new vs reactivated, 2023Q1 exclusive share, 2024Q1 quality removals returning); 38 declined-to-quantify rows in 23 calls | data/processed/abnb_declined_to_quantify.csv | 2026-09-05 | 2026-09-17 | no |
| 13 | Disclosure-behaviour base rate from the same run: management has never quantified a drag from its own product; RNPL negative-effect acknowledgement priced at 0.20 for one print with a strict-reading base rate of 0/4 | docs/pitch-forecasts/questions/rnpl-negative-effect-acknowledged/research-log.md §5 | 2026-09-17 | 2026-09-17 | yes |
| 14 | Team elasticity model: at payout-neutral repricing nights fall only 0.3-1.4% (guest price +0.7%); if hosts do not reprice, nights rise; the transition window (mixed populations) is where the noise lives and it resolves after 15 Sep / 13 Oct | research/notes/host_only_fee_history_and_elasticity.md §3 | 2026-09-06 | 2026-09-17 | no |
| 15 | Web (17 Sep 2026): explainer coverage of the 15 Sep / 13 Oct deadlines and "diversification" advice; CNBC 22 Aug "fee change frustrates hosts"; no measured churn figure and no Airbnb statement on host response; final 72-hour check finds Icons, the $250M Housing Accelerator and fake-listing removals only | sources/web_search_notes_2026-09-17.md | 2026-09-17 | 2026-09-17 | no |
| 16 | No prediction market exists on hosts, listings or fees (Polymarket public-search "Airbnb": Q2 GBV ladders and price-touch markets only) | sources/polymarket_search_Airbnb_20260917T082126Z.json | 2026-09-17 | 2026-09-17 | no |
| 17 | Fee-churn scenario grid (Q2 2026 scale, 50% affected exposure, 50% recapture, 70% contribution margin): 2% incremental churn = -0.5% revenue (-$18M/qtr); 5% = -1.25% (-$45M/qtr); 10% = -2.5% (-$90M/qtr) | data/processed/fee_churn_history/catalyst_scenarios.csv | 2026-09-07 | 2026-09-17 | yes (impact only) |

## 2. Query Log
1. [repo] research/notes/2026-09-07_fee-churn-catalyst.md, 2026-09-07_fee-churn-recent-followup.md, host_only_fee_history_and_elasticity.md (full read)
2. [repo] regex extraction of "active listing|supply grow|listing growth|Supply Our" from all 23 letters, saved to sources/letters_active_listings_supply_passages_4Q20-2Q26.txt
3. [repo] regex extraction of single-fee passages from the 4Q25, 1Q26, 2Q26 letters and calls, saved to sources/fee_migration_passages_4Q25-2Q26.txt
4. [repo] abnb_2025_10k.json grep: "active listings", "fee structure", "service fee", host-loss phrasings (none)
5. [repo] abnb_2026q2_10q.html grep: "active listings", "single service fee", "15.5%", "attract and retain Hosts"
6. [repo] data/processed/overnight/11_supply_economics.csv, 08_supply_index_quarterly.csv
7. [repo] data/processed/fee_churn_recent/pooled_rates.csv; fee_churn_history/catalyst_scenarios.csv; forecast_methods/fee_takerate/03_migrated_share_path.csv
8. [repo] research/notes/2026-09-04_abnb-pitch-catalogue.md grep "listing"
9. [repo] data/processed/abnb_declined_to_quantify.csv grep "listing|supply|host"
10. [repo] docs/pitch-forecasts/questions/rnpl-negative-effect-acknowledged/research-log.md (disclosure base rates)
11. [Polymarket API] public-search?q=Airbnb (2026-09-17T08:21:26Z)
12. WebSearch: Airbnb hosts news September 2026
13. WebFetch: cnbc.com 2026-08-22 fee-change article (HTTP 403; snippet only)
14. WebSearch: Airbnb 15.5% host fee hosts leaving Vrbo direct booking September 15 deadline
15. WebSearch: Airbnb news this week (final 72-hour name-free check; nothing on hosts, listings or fees)

## 3. Leading Hypothesis Entities
Airbnb, Ellie Mertz, Brian Chesky, single service fee, 15.5%, active listings, hosts, Form 10-K, Morgan Stanley

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Observable churn after the 15 Sep / 13 Oct migrations forces an admission on 5 Nov or in February | kept as the main Yes route (P(material churn) 0.25 × P(attribution given churn) 0.35 ≈ 0.09) | No discontinuity after the PMS wave (claim 6); elasticity model says nights barely move at payout-neutral repricing (claim 14); management would attribute any slowdown to "targeted, quality-focused supply" before the fee (claims 3, 12) |
| Management volunteers that some hosts raised prices (lower competitiveness) or paused listings while presenting the migration as net positive | kept, small (0.04) | Mertz has twice said the opposite (hosts did not take up rates); a hedged remark ("a minority of hosts raised prices") is plausible if Q4 ADR runs hot |
| Active-listings growth is disclosed at ≤3% | kept, very small (0.02) | Requires both a collapse and a disclosure; the growth rate has not been printed since 1Q24 and the company drops metrics that stop flattering (claims 1, 2); nights per listing is stable so a collapse would already be in nights (claim 10) |
| The FY26 10-K adds a risk-factor sentence tying host attrition to the fee, and the resolver counts it | priced as resolver risk (0.03) | Convention 1 says a hypothetical "may" sentence is No; the FY25 10-K has no such sentence (claim 4) |
| Morgan Stanley-style question on supply deceleration answered with a fee attribution | discarded as a standalone route | Management's answers on supply attribute pace to strategy (claim 12, 4Q25/1Q26 "deliberate and precise"); folded into the main route |
| Nothing new: positive reiteration, "in line with nights" or silence on listings | base case (about 0.85) | Claims 1-4, 9, 13 |

## 5. Independent Estimates
- base_rate_estimate: 0.08 — management has never attributed a negative to its own product across 23 prints (0/23; Laplace (0+1)/(23+2) = 0.04 per print), two prints plus a 10-K in the window ≈ 1 − (1−0.04)^2 ≈ 0.08; the 2020 migration precedent (claim 9) is a second zero
- decomposition_estimate: 0.18 — 0.25 (material, observable host churn after the mass migration by Jan 2027) × 0.35 (management or a filing attributes it to the fee rather than to strategy, quality or seasonality) = 0.09; + 0.04 (attribution of price increases/pauses without material churn); + 0.02 (≤3% disclosed); + 0.03 (resolver counts a 10-K risk-factor sentence) = 0.18
- anchor_estimate: none — no market on any host or listing statement (claim 16); the nearest internal analogue is C07 at 0.20 for one print with a stricter mechanism
- anchor_value: n/a (NO_EXTERNAL_ANCHOR)
- final_estimate: 0.15 (credible interval 0.08–0.26)
- final_minus_anchor: n/a. The base rate and decomposition are 10 points apart because the decomposition prices the one-off event now under way (the largest forced migration in the company's history, deadlines inside the window) that the historical base rate does not contain; the final sits between them, closer to the decomposition

## 6. Final Numbers
P(Yes) = 0.15; credible interval 0.08–0.26.
Extreme-probability gate: not triggered.
Coherence: B04 ≤ P(any supply-related negative disclosure); if R04 (single-fee accretion stated) resolves Yes, management is framing the migration as a monetisation win, which lowers B04 to about 0.10; the two are negatively correlated for X01.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Convention 1 (10-K risk-factor "may" sentence does not count) | If any new fee-tied host risk sentence counts: 0.30 (Airbnb rewrites risk factors each 10-K and the migration is the year's largest host-facing change) |
| P(material observable churn by Jan 2027) = 0.25 | If the October Inside Airbnb dumps show reviewed-home disappearance ≥ 6% on the 13-market panel (vs 4.2% Jul-Aug): 0.45 → final 0.24; if ≤ 4%: 0.15 → final 0.12 |
| P(attribution given churn) = 0.35 | If management holds the "price more competitively" line regardless (0.15): 0.10 |
| Leg 2 requires a disclosure to exist | If Airbnb resumes printing a listings growth rate in the FY26 10-K (it did not in FY24 or FY25): +0.03 |
| Q4 ADR ex-FX prints ≥ +5% and management attributes part of it to hosts repricing for the fee | 0.22 (a repricing attribution is "lower host pricing competitiveness" on a plain reading) |

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-15 / 2026-10-13 | Migration deadlines (non-EEA / EEA-CH) | No update on the deadline itself; watch host-community volume (r/airbnb_hosts, community.withairbnb.com) for deactivation reports |
| 2026-10-05 to 2026-10-15 | September Inside Airbnb dumps; re-run analysis/src/extend_fee_churn_recent.py on the 13-market panel | Reviewed-home disappearance ≥ 6%: +0.09; ≤ 4%: −0.03 |
| 2026-11-05 | 3Q26 letter, call, 10-Q | Search the letter's Supply paragraph and the 10-Q for "single", "fee", "hosts", "listings"; classify per conventions 1-3; a fee attribution resolves Yes immediately |
| 2026-11-06 to 2026-12-15 | November dumps (first post-deadline month for non-EEA hosts) | Same thresholds as October; this is the first clean read |
| 2027-01-15 | 90-day confirmation of October absences | Persistent-absence rate ≥ 5% (vs 2.3-2.8% in the 2025 panel): +0.10 |
| 2027-02-11 | 4Q26 letter, call; FY26 10-K (same week) | Resolve; if the 10-K is filed later than the print, hold resolution until the filing |

## 9. Impact
If B04 resolves Yes, the acknowledged churn is taken at the scenario grid's middle row (5% incremental churn on 50% affected exposure, 50% recapture; claim 17), which is the smallest effect management would plausibly be forced to name. Deltas versus the memo's base case:

| Item | Delta if B04 happens | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | 0.0 | migration 62% complete in Q3; any effect lands after the deadlines |
| 4Q26 nights (pts) | **−0.5** | half a quarter of the −1.25% revenue effect at 94% migrated, expressed in nights (claim 8, 17) |
| ADR (pts) | 0.0 (±0.5) | hosts absorbing the fee lowers ADR, hosts grossing up raises it; sign unknown |
| 4Q26 revenue ($M) | **−15** (0.5pt × $30M) | brief sensitivity |
| FY27 revenue ($M) | **−195** (−1.25% × ~$15.6bn FY27 team path ≈ 1.3pt of growth × $158M = −$205M) | claim 17; brief sensitivity |
| FY26 adj. EBITDA margin (pp) | **−0.07** (0.5pt × 0.59pp × ¼-year weight) | brief sensitivity (held costs) |
| FY27 adj. EBITDA margin (pp) | **−0.85** (0.66 × 1.3) | brief sensitivity |
| FY27 EPS ($) | **−0.18** ($195M × 0.66 flow-through = $129M EBITDA × $0.0014) | brief sensitivity |
| Stock ($/share) | **−6.4** (1.3pt of FY27 nights × $4.90 joint solve; −$2.0 on a fixed multiple) | brief sensitivity |
| **EV = P × impact** | **0.15 × −$6.4 = −$0.96/share** (−$0.3 on the fixed multiple) | |
| Materiality | **Immaterial at the memo's $1/share bar (borderline).** Carry it as one sentence on the supply-side risk of the migration, not as a number; if the October/November dumps move P above 0.25 it becomes material | |

## RESUME
The next agent (audit response) should attack three things: (1) the 0.25 for "material observable churn", which rests on the PMS-wave null and the elasticity model, against the fact that the September/October waves hit individual hosts who reprice less reliably than property managers; (2) convention 1, since an auditor may argue a 10-K sentence saying the transition "has caused some hosts to raise prices" is exactly what the question asks and is a routine MD&A construction; (3) the impact row's 50% recapture. If the September Inside Airbnb dumps have landed, re-run `analysis/src/extend_fee_churn_recent.py` and apply the section-7 thresholds before anything else.
