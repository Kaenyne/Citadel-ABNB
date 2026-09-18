# RESEARCH LOG

Revision 2 (2026-09-17, audit response to A15, Fable). Revision 1 (2026-09-17, initial forecast, Fable). Batch A15 (B04, B05, B06, B07 share the web budget accounting; each log carries its own complete claims ledger and query log). No script is needed to reproduce the numbers: every computation is a one-line product or sum shown in section 5 and section 9; the audit's reproduction script `docs/pitch-forecasts/audits/A15-reproduce.py` replays the base-rate, decomposition and impact arithmetic.

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
- revision: 2
- revised: 2026-09-17
- agent: fable
- batch: A15
- audit: `docs/pitch-forecasts/audits/A15-research-audit.md` (independent Opus auditor standing in for Codex); response `docs/pitch-forecasts/audits/A15-audit-response.md`

## 0b. Question (verbatim)
### Title
By the Feb print, will management or the 10-K/10-Q attribute slower active-listing growth, host attrition, or lower host pricing competitiveness to the single-fee migration, or disclose active listings growth ≤ +3% y/y?
### Resolution Criteria
**Type.** Binary. **Resolution.** Yes on either. Resolution ~11 Feb 2027.
### Fine Print
None given in the registry. Conventions adopted (each priced as a resolver risk in section 7):
1. Leg 1 (attribution) requires a statement of an observed or expected effect that the company itself ties to the single-fee migration: e.g. "some hosts chose to leave the platform / paused listings after the fee change", "supply growth moderated as hosts adjusted to the single fee", "hosts raised prices to offset the fee, which made listings less competitive". A forward-looking risk-factor sentence ("the transition ... may cause some hosts to raise prices or discontinue hosting") in the 10-K/10-Q is hypothetical boilerplate and resolves No. A statement that hosts *absorbed* the fee (lower guest prices) is the opposite sign and resolves No. A concession in the "yes, some hosts left / raised prices, but the net effect is positive" form (the RNPL template, claim 13) names an observed negative and resolves **Yes**; the net-positive framing does not rescue it.
2. Leg 2 (≤ +3%) requires a numeric or bucket disclosure that implies ≤3% ("low single digits", "approximately 3%", "flat"). The standing sentence "active listings grew relatively in line with Nights and Seats Booked" resolves No while nights grow above 3%. A level-only disclosure ("over 9 million") resolves No.
3. Window and documents: the 5 Nov 2026 letter, call and 3Q26 10-Q; the ~11 Feb 2027 letter and call; the FY26 10-K if filed by the Feb print or within the same week (the FY25 10-K was filed on the print day, 12 Feb 2026, so the 10-K is treated as part of the February opportunity, not a third independent one); conference appearances and 8-Ks between 17 Sep 2026 and the Feb print. Letter governs over call where they differ.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Active-listings growth was last disclosed as a percentage in 1Q24 (+15%; +17% **excluding experiences**); from 1Q25 every letter says supply grew "approximately in line with" or "slightly above" Nights and Seats Booked (i.e. 8-10%); 4Q25 "over 9 million"; the 2Q26 letter contains no active-listings sentence at all (0 hits), only "our supply strategy is deliberate and precise" and 150,000 World Cup listings | sources/letters_active_listings_supply_passages_4Q20-2Q26.txt; data/raw/letters/*.htm; docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md §4; A15-reproduce.py (regex over 23 letters) | 2026-08-06 | 2026-09-17 | yes |
| 2 | Airbnb "has form for dropping metrics that stop flattering": 1BR-vs-hotel comparison ended after 4Q23, long-term-stay share and cross-border share after 1Q24, listings growth after 1Q24 | docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md §6 row 7 | 2026-09-11 | 2026-09-17 | yes |
| 3 | Management framing of the migration is uniformly positive on the record: 4Q25 call (Mertz, to Kopelman): "we obviously very diligently managed the communication with our hosts to ensure that they did not perceive this as a fee increase ... many of the hosts did not take up their rates. Instead, the effective ADR to guests came down modestly"; 1Q26 call: "will help our hosts price more competitively"; 2Q26 call: "helped our host price more competitively and provided greater price transparency. As a result of its success, we recently announced the broader rollout ... Approximately half of our active listings are now subject to the single service fee"; 2Q26 Chesky: "we haven't really gotten much feedback from our core hosts. Mostly, they just want to make sure their bookings are going up, and our results show they are". Analysts asked about the fee on each of the three calls (Kopelman 4Q25, Jed Kelly 2Q26) but none asked about host attrition directly | sources/fee_migration_passages_4Q25-2Q26.txt; data/raw/transcripts/web/4Q25.html, 1Q26.html, 2Q26.html | 2026-08-06 | 2026-09-17 | yes |
| 4 | The FY25 10-K describes the single-fee transition neutrally in the revenue-recognition note ("In October 2025, the Company began transitioning to a single-fee structure, charging only the host a service fee") and lists "the service fees we charge" among host-competition factors; it contains no host-attrition risk sentence tied to the fee and no active-listings growth figure ("no single city ... more than 1% of our active listings"). It was filed 12 Feb 2026, the day of the 4Q25 print | data/raw/regulatory/quantification/abnb_2025_10k.json; data/processed/overnight2/D/rnpl_statement_ledger.csv (D054, dated 2026-02-12) | 2026-02-12 | 2026-09-17 | yes |
| 5 | The 2Q26 10-Q carries no fee-migration host language beyond forward-looking-statement boilerplate ("our ability to attract and retain hosts and guests") | data/raw/regulatory/quantification/abnb_2026q2_10q.html | 2026-08-06 | 2026-09-17 | no |
| 6 | Team fee-churn panel: the October 2025 PMS migration produced no disappearance spike (11 markets: 4.10% Sep-Oct, 3.03% Oct-Nov, 3.43% Nov-Dec); the Dec-Jan 12.74% spike is a capture-composition artefact (zero previous-scrape rows; 65-90% of missing IDs reappear); 13-market Jun-Jul 3.63% and Jul-Aug 4.14% all-ID disappearance with longer intervals, "does not establish acceleration"; **reviewed-home** panel rates 3.32% (Jun-Jul, 9-23-day intervals) and 4.20% (Jul-Aug, 38-50-day intervals). London (UK hosts migrated 22 Jun): all-ID 5.12% / 4.95%, **reviewed-home 5.63% / 6.38%** — the highest market in the panel in both windows. London's June baseline vintage is 19 Jun, three days before the transition, so the panel holds **no pre-transition London window**; London's Jun-Jul → Jul-Aug change (+0.75pp on reviewed homes, interval 22 → 38 days) is smaller than the 13-market change (+0.88pp pooled, +1.06pp equal-market mean, intervals roughly doubling), so the London level is a market fixed effect plus an unknown migration effect, not a measured treatment effect; the source note calls it "descriptive diagnostics, not treated-versus-control estimates" | research/notes/2026-09-07_fee-churn-catalyst.md; research/notes/2026-09-07_fee-churn-recent-followup.md:24; data/processed/fee_churn_recent/pooled_rates.csv, market_rates.csv | 2026-09-07 | 2026-09-17 | yes |
| 7 | Direct host-response evidence is anecdotal: one listing (31054261) steering guests to a competitor over the 15.5% fee; four Reddit accounts of final stays/deactivations (1 Sep 2026); explicit fee-related exit intentions (Jul 2026); none independently matched to a completed, fee-caused delisting | research/notes/2026-09-07_fee-churn-recent-followup.md table F01-F10 | 2026-09-07 | 2026-09-17 | no |
| 8 | Remaining hosts migrate by 15 Sep 2026 (non-EEA) and 13 Oct 2026 (EEA/CH); the team's migrated-share path is 62% of listings in 3Q26 and 94% in 4Q26; meaningful 90-day disappearance confirmation for Oct-Nov absences arrives "around January/February 2027 or later" | research/notes/2026-09-07_fee-churn-catalyst.md; data/processed/forecast_methods/fee_takerate/03_migrated_share_path.csv | 2026-09-07 | 2026-09-17 | yes |
| 9 | The 2019-2020 forced host-only migration (mandatory Dec 2020 outside the Americas) produced no published attrition or listing-count effect; Airbnb's only number was "+17% bookings" for hosts who "priced competitively" | research/notes/host_only_fee_history_and_elasticity.md §1 | 2026-09-06 | 2026-09-17 | yes |
| 10 | Nights per average active listing has been 62.5-62.7 for four years (2022-25), so listings growth co-moves with nights; a genuine collapse in listings growth would be visible in nights within quarters | docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md §2; data/processed/overnight/11_supply_economics.csv | 2026-09-11 | 2026-09-17 | yes |
| 11 | Morgan Stanley (Nowak, Underweight, PT $125, 30 Jul 2026) argues active-listings growth slowed from ~12% (2018-22) to ~7%; the debate is live on the Street, so an analyst question on supply is likely on both calls | research/notes/2026-09-04_abnb-pitch-catalogue.md (Morgan Stanley entry) | 2026-09-04 | 2026-09-17 | no |
| 12 | Management has declined to quantify supply detail repeatedly (2022Q2 listings ex-China, 2022Q4 new vs reactivated, 2023Q1 exclusive share, 2024Q1 quality removals returning); 38 declined-to-quantify rows in 23 calls | data/processed/abnb_declined_to_quantify.csv | 2026-09-05 | 2026-09-17 | no |
| 13 | **Management has conceded a negative of its own product on the record in 3 of 23 prints, always in the "yes, but net positive" form, and always about RNPL cancellations:** 3Q25 call D006 (Mertz: "Yes, there are increased cancellations, but we're highly confident that the net impact of the product is a lift to net bookings"; letter D009 "we expect some cancellations closer to the date of stay"); 4Q25 call D017/D018 (quantified: "the aggregate nominal increase in cancellations rate, it's approximately 1%", "16% cancellation rate historically going to 17%"); 1Q26 call D035 ("Certainly with the offering, there's a very elevated level of cancellations that come with the program. Across all regions, what we see is that the net impact is positive"). The fee-specific record is 0 of 3 prints (4Q25, 1Q26, 2Q26). The RNPL cancellations are a designed, measured mechanic conceded when asked; host attrition would be a strategic failure with a ready alternative attribution (quality removals, "deliberate and precise" supply). C07 (RNPL negative-effect acknowledged, 5 Nov only, a stricter mechanism: escalation beyond the conceded baseline) is at **0.27** (revision 2) | data/processed/overnight2/D/rnpl_statement_ledger.csv (D006, D009, D017, D018, D035); docs/pitch-forecasts/questions/rnpl-negative-effect-acknowledged/research-log.md §5 (rev 2); forecasts/2026-09-17-forecast.json (rev 2, p 0.27) | 2026-09-17 | 2026-09-17 | yes |
| 14 | Team elasticity model: at payout-neutral repricing nights fall only 0.3-1.4% (guest price +0.7%); if hosts do not reprice, nights rise; the transition window (mixed populations) is where the noise lives and it resolves after 15 Sep / 13 Oct | research/notes/host_only_fee_history_and_elasticity.md §3 | 2026-09-06 | 2026-09-17 | no |
| 15 | Web (17 Sep 2026): explainer coverage of the 15 Sep / 13 Oct deadlines and "diversification" advice; CNBC 22 Aug "fee change frustrates hosts" (HTTP 403, snippet only); no measured churn figure and no Airbnb statement on host response **in the searches recorded**; final 72-hour check found Icons, the $250M Housing Accelerator and fake-listing removals only | sources/web_search_notes_2026-09-17.md | 2026-09-17 | 2026-09-17 | no |
| 16 | No prediction market exists on hosts, listings or fees (Polymarket public-search "Airbnb": Q2 GBV ladders and price-touch markets only) | sources/polymarket_search_Airbnb_20260917T082126Z.json | 2026-09-17 | 2026-09-17 | no |
| 17 | Fee-churn scenario grid (Q2 2026 scale, 50% affected exposure, 50% recapture, 70% contribution margin): 2% incremental churn = -0.5% revenue (-$18.0M/qtr); 5% = -1.25% (-$45.1M/qtr); 10% = -2.5% (-$90.2M/qtr) | data/processed/fee_churn_history/catalyst_scenarios.csv | 2026-09-07 | 2026-09-17 | yes (impact only) |

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
16. [rev 2, repo] data/processed/overnight2/D/rnpl_statement_ledger.csv: every row whose quote contains "cancel" (21 rows), to count the prints in which management conceded an own-product negative (3Q25, 4Q25, 1Q26)
17. [rev 2, repo] data/processed/fee_churn_recent/market_rates.csv: London reviewed-home rows (baseline vintages 19 Jun and 16 Jul; intervals 22 and 38 days) and the 13-market reviewed-home matrix for both windows
18. [rev 2, repo] docs/pitch-forecasts/questions/rnpl-negative-effect-acknowledged/forecasts/2026-09-17-forecast.json (revision 2, p 0.27); risk-single-fee-take-rate-accretion-stated (R04 rev 2, p 0.52)
19. [rev 2, repo] docs/pitch-forecasts/audits/A15-reproduce.py run from the repo root (`py -3.13 -B`), output in `A15-reproduce.stdout.txt`

## 3. Leading Hypothesis Entities
Airbnb, Ellie Mertz, Brian Chesky, single service fee, 15.5%, active listings, hosts, Form 10-K, Morgan Stanley, Reserve Now Pay Later (as the disclosure template)

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Observable churn after the 15 Sep / 13 Oct migrations forces an admission on 5 Nov or in February | kept as the main Yes route (P(material churn) 0.30 × P(attribution given churn) 0.45 ≈ 0.135) | No discontinuity after the PMS wave (claim 6); elasticity model says nights barely move at payout-neutral repricing (claim 14); London reads 1.5x the panel on the trigger metric but with no pre-period and a smaller month-on-month change than the panel (claim 6); when a product side-effect exists and is asked about, management has conceded it 3 of 3 times while framing it net positive (claim 13), but it has an alternative attribution for supply ("deliberate and precise", quality removals; claims 3, 12) that RNPL cancellations never had |
| Management volunteers that some hosts raised prices (lower competitiveness) or paused listings while presenting the migration as net positive | kept, small (0.05) | Mertz has twice said the opposite (hosts did not take up rates); a hedged remark ("a minority of hosts raised prices, but net bookings are up") is the RNPL template applied to pricing and is plausible if Q4 ADR runs hot |
| Active-listings growth is disclosed at ≤3% | kept, very small (0.02) | Requires both a collapse and a disclosure; the growth rate has not been printed since 1Q24 and the company drops metrics that stop flattering (claims 1, 2); nights per listing is stable so a collapse would already be in nights (claim 10) |
| The FY26 10-K adds a risk-factor sentence tying host attrition to the fee, and the resolver counts it | resolver risk, priced in §7 only (removed from the point estimate at revision 2) | Convention 1 says a hypothetical "may" sentence is No; the FY25 10-K has no such sentence (claim 4) |
| Morgan Stanley-style question on supply deceleration answered with a fee attribution | discarded as a standalone route | Management's answers on supply attribute pace to strategy (claim 12, 4Q25/1Q26 "deliberate and precise"); folded into the main route's 0.45 |
| Nothing new: positive reiteration, "in line with nights" or silence on listings | base case (about 0.79) | Claims 1-4, 9; the fee-specific 0/3 record in claim 13 |

## 5. Independent Estimates
- base_rate_estimate: 0.20 — management has conceded an own-product negative in 3 of 23 prints (3Q25, 4Q25, 1Q26, all RNPL cancellations; claim 13; revision 1's "0/23" was false); Laplace (3+1)/(23+2) = 0.16 per print; two opportunities in the window (5 Nov; ~11 Feb with the FY26 10-K filed the same day, so not independent) → 1 − (1−0.16)² = 0.29; discounted by about 0.7 because every conceded case was a designed, measured mechanic conceded when asked, whereas a supply or pricing effect of the fee has a ready alternative attribution and the fee-specific record is 0 of 3 prints (Laplace 0.20 per print) → **0.20**. The 2020 migration precedent (claim 9) is a further zero
- decomposition_estimate: 0.20 — 0.30 (material, observable host churn after the mass migration by Jan 2027; up from 0.25 because the one individual-host migration on the record, London, reads 5.6-6.4% reviewed-home disappearance against a 3.3-4.2% panel, with the caveats in claim 6) × 0.45 (management or a filing attributes it to the fee rather than to strategy, quality or seasonality; up from 0.35 because the RNPL template shows the modal answer to a direct question concedes the negative inside a net-positive frame, which resolves Yes under convention 1) = 0.135; + 0.05 (attribution of price increases/pauses without material churn); + 0.02 (≤3% disclosed); union 1 − (1−0.135)(1−0.05)(1−0.02) = **0.195**. The revision-1 +0.03 resolver branch (10-K "may" sentence counted) is removed from the point and stays in §7
- anchor_estimate: none — no market on any host or listing statement (claim 16); the nearest internal analogue is C07 at **0.27** (revision 2) for one print with a stricter mechanism (escalation beyond a conceded baseline); B04 has two prints plus the filings and a deadline inside the window but a mechanism management can attribute elsewhere; the analogue says the order of magnitude is right, not the direction
- anchor_value: n/a (NO_EXTERNAL_ANCHOR)
- final_estimate: 0.21 (credible interval 0.12–0.33)
- final_minus_anchor: n/a. The base rate and decomposition now agree at 0.20 from different constructions (a discounted per-print concession rate vs the churn-then-attribution pipeline); the final sits a point above them for the deadline inside the window. Audit A15's independent 0.24 (Nov 0.06, Feb 0.16, leg 2 0.02, 10-K MD&A 0.03 → 0.249) differs by 3 points: it prices a non-hypothetical 10-K MD&A sentence at 0.03 as a route, which this log carries as resolver risk in §7 rather than in the point

## 6. Final Numbers
P(Yes) = 0.21; credible interval 0.12–0.33.
Extreme-probability gate: not triggered.
Coherence: B04 ≤ P(any supply-related negative disclosure); if R04 (single-fee accretion stated, rev 2 p 0.52) resolves Yes, management is framing the migration as a monetisation win, which lowers B04 to about 0.15; the implied No-branch is about 0.27; the two are negatively correlated for X01. C07 (0.27, one print) and B04 (0.21, two prints, harder mechanism) are consistent.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Convention 1 (10-K risk-factor "may" sentence does not count) | If any new fee-tied host risk sentence counts: 0.33 (Airbnb rewrites risk factors each 10-K and the migration is the year's largest host-facing change); a non-hypothetical MD&A sentence ("the transition has caused some hosts to raise prices") already resolves Yes under convention 1 and is inside the 0.05 pricing route |
| P(material observable churn by Jan 2027) = 0.30 | If the October Inside Airbnb dumps show reviewed-home disappearance ≥ 6% on the 13-market panel (vs 4.2% Jul-Aug): 0.50 → final 0.29; if ≤ 4%: 0.18 → final 0.16 |
| P(attribution given churn) = 0.45 | If management holds the "price more competitively" line regardless (0.25): 0.15; if the RNPL template applies in full (0.65): 0.27 |
| Base-rate class | Fee-specific record only (0/3, Laplace 0.20 per print, undiscounted over two prints = 0.36): final 0.25; all-print rate without the 0.7 discount (0.29): final 0.24 |
| Leg 2 requires a disclosure to exist | If Airbnb resumes printing a listings growth rate in the FY26 10-K (it did not in FY24 or FY25): +0.03 |
| Q4 ADR ex-FX prints ≥ +5% and management attributes part of it to hosts repricing for the fee | 0.28 (a repricing attribution is "lower host pricing competitiveness" on a plain reading) |
| London's 6.4% is a migration effect rather than a market fixed effect | If a Sep-Oct London reviewed-home reading ≥ 6.5% arrives with the panel ex-London flat: P(churn) 0.40 → final 0.25 |

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-15 / 2026-10-13 | Migration deadlines (non-EEA / EEA-CH) | No update on the deadline itself; watch host-community volume (r/airbnb_hosts, community.withairbnb.com) for deactivation reports |
| 2026-10-05 to 2026-10-15 | September Inside Airbnb dumps; re-run analysis/src/extend_fee_churn_recent.py on the 13-market panel and the London rows | Reviewed-home disappearance ≥ 6% on the panel: +0.08; ≤ 4%: −0.05; London alone ≥ 6.5% with the panel ex-London flat: +0.04 |
| 2026-11-05 | 3Q26 letter, call, 10-Q | Search the letter's Supply paragraph and the 10-Q for "single", "fee", "hosts", "listings"; classify per conventions 1-3; a fee attribution in any form, including "some hosts ... but net positive", resolves Yes immediately |
| 2026-11-06 to 2026-12-15 | November dumps (first post-deadline month for non-EEA hosts) | Same thresholds as October; this is the first clean read |
| 2027-01-15 | 90-day confirmation of October absences | Persistent-absence rate ≥ 5% (vs 2.3-2.8% in the 2025 panel): +0.10 |
| 2027-02-11 | 4Q26 letter, call; FY26 10-K (same day, per the FY25 precedent) | Resolve; if the 10-K is filed later than the print, hold resolution until the filing |

## 9. Impact
Yes is a union of routes with different consequences, so the table is route-weighted (A15-15). The churn route carries 0.135 of the 0.195 union (share 0.69): its acknowledged churn is taken at the mean of the scenario grid's 2% and 5% rows (−0.875% of revenue; claim 17), since a disappearance reading of about 6% against a 4.2% baseline is between the two. The other routes (share 0.31: a pricing-competitiveness attribution or a ≤3% disclosure with no measured churn) carry about a fifth of that effect. Deltas versus the memo's base case:

| Item | Churn route (share 0.69) | Other routes (share 0.31) | **E[delta \| Yes]** | Source / computation |
|---|---|---|---|---|
| 3Q26 nights (pts) | 0.0 | 0.0 | **0.0** | migration 62% complete in Q3; any effect lands after the deadlines |
| 4Q26 nights (pts) | −0.35 | −0.10 | **−0.27** | half a quarter of the −0.875% revenue effect at 94% migrated, in nights (claims 8, 17) |
| ADR (pts) | 0.0 (±0.5) | 0.0 | **0.0** | hosts absorbing the fee lowers ADR, hosts grossing up raises it; sign unknown |
| 4Q26 revenue ($M) | −10 | −3 | **−8** | 0.35pt × $30M |
| FY27 revenue ($M) | −137 | −15 | **−99** | −0.875% × ~$15.6bn FY27 team path ≈ 0.87pt of growth × $158M |
| FY26 adj. EBITDA margin (pp) | −0.05 | −0.01 | **−0.04** | 0.35pt × 0.59pp × ¼-year weight (held costs) |
| FY27 adj. EBITDA margin (pp) | −0.57 | −0.06 | **−0.42** | 0.66 × 0.87 |
| FY27 EPS ($) | −0.13 | −0.01 | **−0.09** | $137M × 0.66 flow-through = $90M EBITDA × $0.0014 |
| Stock ($/share) | −4.3 (0.87pt of FY27 nights × $4.90 joint solve; −1.3 on a fixed multiple) | −1.0 | **−3.3** (−1.1 fixed multiple) | brief sensitivity |
| **EV = P × E[impact \| Yes]** | | | **0.21 × −$3.3 = −$0.70/share** (−$0.24 on the fixed multiple) | |
| Materiality | | | **Immaterial at the memo's $1/share bar, cleanly** (revision 1's borderline −$0.96 booked the full 5%-churn scenario against every route). Carry it as one sentence on the supply-side risk of the migration, not as a number; it becomes material only if the October/November dumps take P above 0.30 *and* the disappearance reading is at or above the 5% row | |

## 10. Revision notes
| Change | Finding |
|---|---|
| Metadata: revision 2, revised 2026-09-17; audit and response paths added | — |
| Claim 13 rewritten: "0/23" withdrawn; management conceded an own-product negative in **3 of 23** prints (3Q25 D006/D009, 4Q25 D017/D018, 1Q26 D035 — the audit counted two; D035 is the third), all in the "yes, but net positive" form; convention 1 now says that form resolves Yes; base-rate route rebuilt at 0.20 from Laplace 0.16/print over two opportunities with a stated 0.7 discount | A15-01, A15-18 |
| Claim 13 and §5: C07 quoted at its revision-2 value 0.27 (was 0.20) with the direction it implies stated | A15-08 |
| Claim 6: London reviewed-home rates 5.63% / 6.38% added beside the all-ID rates; the absence of a pre-transition London window and the smaller-than-panel month-on-month change recorded; P(material churn) 0.25 → 0.30 (not the audit's 0.35, for those two reasons) | A15-07 |
| Decomposition: P(attribution \| churn) 0.35 → 0.45 on the RNPL template; pricing route 0.04 → 0.05; the +0.03 resolver branch removed from the point and left in §7; union stated as 1 − Π(1−p) = 0.195 | A15-01, A15-16 |
| Convention 3: the FY26 10-K treated as part of the February opportunity (FY25 10-K filed 12 Feb 2026, the print day), so two opportunities, not three | A15-18 |
| Claim 1: "+17% ex quality removals" → "+17% excluding experiences" | A15-17 |
| Claim 15: "no measured churn figure ... in the searches recorded" | A15-25 |
| §9 rebuilt route-weighted with E[impact \| Yes]; churn scenario at the mean of the 2% and 5% rows; EV −$0.96 → −$0.70; materiality "borderline" → "immaterial, cleanly" | A15-15 |
| §7 and §8 thresholds recomputed on the revision-2 parameters; London-specific sensitivity and monitoring row added | A15-07 |
| Final 0.15 (0.08–0.26) → **0.21 (0.12–0.33)**; audit's independent 0.24 differs by 3 points (its 0.03 MD&A route is carried here as resolver risk) | A15-01, A15-07, A15-08, A15-16 |

## RESUME
The next agent should (1) re-run `analysis/src/extend_fee_churn_recent.py` when the September/October Inside Airbnb dumps land and apply the §7/§8 thresholds, reading London against the panel ex-London rather than as a level; (2) on 5 Nov, search the letter's Supply paragraph, the call's fee answers and the 10-Q for any "some hosts ... but" construction, which resolves Yes under convention 1 as revised; (3) keep the 50% recapture in the impact row under review — it is the largest untested parameter in §9. The audit's independent 0.24 and this log's 0.21 differ only on where the non-hypothetical 10-K MD&A route sits (point vs §7); no further reconciliation is needed unless the FY26 10-K draft language leaks through a conference appearance.
