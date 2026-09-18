**B04 — submitted probability: 0.15, interval 0.08–0.26.**
Defensible as written: no. The number is too low and the base rate under it is factually wrong.
First fix: "management has never attributed a negative to its own product across 23 prints (0/23)" is false — Mertz conceded RNPL cancellations on the 3Q25 call and quantified them (16% → 17%) on the 4Q25 call.
Next fix: quote London's reviewed-home disappearance (5.63% / 6.38%), which is already above the log's own ≥6% trigger, and move the 10-K resolver branch out of the point estimate.
Independent comparison: **0.24** (0.14–0.38); the immaterial verdict survives and strengthens once the impact table is conditioned properly.

**B05 — submitted probability: 0.68, interval 0.50–0.82.**
Defensible as written: the headline is inside my interval; the base rate that carries half of it is not.
First fix: the Poisson rate is non-stationary — all six qualifying events fall in Nov 2024–Dec 2025 and **zero** clear the log's own gate in the trailing 8.5 months; the recency-honest base rate is 0.33–0.55, not 0.70.
Next fix: the decomposition product is 0.712, not 0.73; and convention 2 ("or taking effect in the window") is written down and then never used, which is the largest single uncertainty in the number.
Independent comparison: **0.62** (0.42–0.80); on a surprise basis the EV is −$0.80/share, so the "material" flag should come off.

**B06 — submitted probability: 0.35, interval 0.22–0.48.**
Defensible as written: the headline is within 2 points of mine, reached by a base rate I do not accept.
First fix: 1Q22 is a risk list, not an attribution — the base rate is 2 of 8 (0.30), not 3 of 8 (0.40), and the denominator is chosen partly by whether management talked about the conflict.
Next fix: repair §9 — 3Q26 is printed before resolution, so the −0.7pt nights row double-counts against the nowcast, and the "1Q26 +0.7%" support is −1.6% on the excess convention the comparison base rate uses.
Independent comparison: **0.33** (0.20–0.47); immaterial, and the log is right that this is a risk to the short's narrative rather than a bonus item.

**B07 — submitted probability: 0.58, interval 0.42–0.72.**
Defensible as written: no — two sign errors cancel, and the number lands roughly right for the wrong reasons.
First fix: the Q3 2026 input of −6.5% contradicts the data (September 2025 was −7.69%, the *easiest* comp of the quarter; holding July's stack gives −5.75%).
Next fix: the decomposition calls a 1.9pp improvement in the two-year stack "persistence", and §5 calls a harder comp "the easier-than-Q3 comparison" in the same sentence in which it correctly calls it a headwind.
Independent comparison: **0.63** (0.47–0.77); the impact table needs no work — the question is immaterial under any weighting.

## Scope and verification

Audit date **2026-09-17**, read-only, revision 1 of all four logs. `py -3.13` (pandas 3) recomputed every base rate below from the repository files; no network was used, so every external claim was checked against the saved `sources/` snapshots. No prohibited directory was opened. I wrote only this file and `A15.done`.

All four datasets replay. `ntto_q4_persistence.csv` reproduces from `data/processed/q3nowcast/G/raw/ntto_arrivals_monthly.csv` to **0.00** maximum absolute difference across all 18 rows and 7 columns; its summary statistics recompute to mean **−0.49 / −1.00 / −2.25** and sd **4.04 / 6.34 / 7.43** for Q4−Q3, Q4−Jul and Q4−Q2, matching claim 5. `letter_geopolitical_base_rate_4Q20-2Q26.csv` reproduces row-for-row from a regex sweep of all 23 letters, and every quoted outlook sentence verifies verbatim. `eurostat_country_shares_scaled_to_emea.csv` matches claim 2's shares exactly (FR 22.34, ES 19.91, IT 14.58, DE 7.18, EL 5.48, PT 5.20, PL 4.66, HR 4.41, AT 2.61, NL 1.25, IE 0.88). `regulatory_market_inventory.csv` carries every Inside Airbnb count in claim 3 (Paris 77,679; London 92,799; Madrid 22,835; Lisbon 17,098; Barcelona 15,406; Athens 14,342; Florence 13,508; Amsterdam 10,465) and the INE ratios (Canaries 48,356 / 341,001 = 14.2%; Balearics 6.2%).

Every B07 headline figure reproduces from the NTTO cache: Jan–Jul 2026 monthly y/y **−4.21, +0.79, +3.56, −14.12, −6.54, −1.85, −7.02**; 1Q26 **−0.05%**, 2Q26 **−7.67%**, 3Q25 **−4.40%**, 4Q25 **−2.55%** (Oct −3.12, Nov −3.47, Dec −1.28); Jan–Jul **18.328m vs 19.240m, −4.74%**; 4Q25 two-year stack **+3.22%** against 4Q24 y/y **+5.93%**; 2026 two-year stacks **+0.93, −1.68, −8.49, −7.24, −9.11, −5.18, −9.89**; and every regional share and y/y in claim 4 to two decimals.

Three arithmetic checks pass and one fails. B07's §5 normal evaluations are correct (Φ(0.50) = 0.6915, Φ(0.5556) = 0.7108, Φ(0.60) = 0.7257, the four-way blend 0.6575 ≈ 0.65; the scenario mixture 0.55 Φ(0.3) + 0.30 Φ(−0.75) + 0.15 Φ(1.6) = **0.5496**), and its stack-to-y/y conversions reproduce (−8 → −5.59, −6 → −3.54, −10.5 → −8.16). B05's Poisson arithmetic reproduces (λ = 6 × 4.83/24 = 1.207, P = **0.701**; strict 0.553; lenient 0.927; the window is 147 days = 4.830 months). B05's decomposition product does **not** reproduce (finding A15-11). All four binaries clear the extreme-probability gate; all four EV lines are arithmetically right given their inputs (0.15 × 6.4 = 0.96; 0.68 × 2.5 = 1.70; 0.35 × 1.5 = 0.525; 0.58 × 0.2 = 0.116).

Cross-question coherence inside and outside the batch holds where it is checkable. B06 claim 11's "P(4Q26 bucket ≤ high single digits) = 0.61" is exactly C02 revision 2's (c) 0.30 + (d) 0.31. B06's conditional on B01 (0.34) implies an unconditional 0.30 on the No-branch, consistent with 0.35. B04's conditional on R04 (0.52) implies 0.20 on the No-branch, consistent with 0.15. B04's cited C07 value is stale (A15-08).

Paths below are relative to `docs/pitch-forecasts/questions/`; **B04**, **B05**, **B06** and **B07** name their folders, and `log`, `forecast` mean `research-log.md` and `forecasts/2026-09-17-forecast.json`.

## Findings

| id | question | severity | file:line or field | what is wrong | how you verified | proposed fix |
|---|---|---|---|---|---|---|
| A15-01 | B04 | critical | `log:84` (base_rate_estimate); claim 13; `forecast.estimates.base_rate` | The base rate rests on a false premise: "management has never attributed a negative to its own product across 23 prints (0/23)". Management has done exactly that, twice, on the record — and quantified it. This is the single number that holds B04 down, and the log's own claim 13 cites the question (C07) that exists because the premise is false. | `data/processed/overnight2/D/rnpl_statement_ledger.csv`: **D006** (3Q25 call, 6 Nov 2025, Mertz) "Yes, there are increased cancellations, but we're highly confident that the net impact of the product is a lift to net bookings"; **D017** (4Q25 call, 12 Feb 2026) "the aggregate nominal increase in cancellations rate … is approximately 1%"; **D018** "an average of maybe 16% cancellation rate historically going to 17%"; **D009** (3Q25 letter) "we expect some cancellations closer to the date of stay". | Replace 0/23 with **2/23** prints (Laplace 3/25 = 0.12 per print; two prints ≈ 0.226). More important than the count: D006 is the *template*. "Yes, some hosts left, but the net effect is positive" is the modal answer to an analyst question on the fee, and under the log's own convention 1 it resolves **Yes**. Rebuild the base-rate route at ~0.20 and the final at ~0.24. |
| A15-02 | B07 | critical | `log:75` (base_rate_estimate); `forecast.estimates.base_rate_construction` | The 3Q26 input "≈ −6.5% (Jul −7.0 preliminary; August unknown; September faces a −7.7% comp)" inverts the comp. September 2025 was **−7.69%** — the weakest month of 3Q25 and therefore the *easiest* comparison of 3Q26, not a headwind. The entire base-rate route (0.69 / 0.71 / 0.73 / 0.50 → 0.65) is centred on it. | Recomputed monthly 2025 y/y from the cache: Jul −3.09, Aug −2.85, **Sep −7.69**, Oct −3.12, Nov −3.47, Dec −1.28. Holding July's two-year stack (−9.89%) through August and September gives 3Q26 **−5.75%**; a Q3 of −6.5% requires the stack to deteriorate to **−11.0%**, 1.1pp worse than any month of 2026. | Re-centre on 3Q26 = −5.75%: centre −6.24, sd 4.04 → **P = 0.621**, not 0.69. Say plainly that August and September are unknown and that September's comp is the easiest of the quarter. |
| A15-03 | B07 | critical | `log:76,80`; `forecast.estimates.decomposition_construction` | Two compounding errors in the decomposition, both pushing the number down. (i) The "persist −8" scenario, at 0.55 weight, sets the two-year stack **1.9pp better** than the latest reading (July −9.89%) — it is a normalisation scenario labelled persistence. (ii) §5 calls the 4Q25 base "the easier-than-Q3 comparison" in the same sentence in which it correctly calls it "a 1.9pp headwind"; a base of −2.55% is a *harder* comp than −4.40%, so the decomposition, done honestly, should land **above** the persistence route, not 8 points below it — which reverses the stated reason for leaning to 0.57. | Three independent centres for 4Q26 y/y, all recomputed from the cache: aggregate constant July stack **−7.53%**; regional constant July stack (nine regions, 4Q25 weights) **−7.08%**; 4Q25-share-weighted July y/y **−6.83%**. The log's own mixture centre is 0.55(−5.6) + 0.30(−3.5) + 0.15(−8.2) = **−5.36%**. | Re-weight around a centre of **−6.8%**. Keep the three-scenario shape but set the stacks at −9.9 (persist, the actual latest reading), −8.0 (normalise) and −11.5 (deteriorate). Correct the §5 sentence: the Q4 comp is *harder*, which is an argument for a higher probability. |
| A15-04 | B05 | critical | `log:88` (base_rate_estimate); `datasets/qualifying_events_trailing_24m.csv`; `forecast.estimates.base_rate_construction` | The Poisson rate is assumed stationary and is not. All six qualifying events are dated Nov 2024 – Dec 2025. Under the log's **own** gate, **zero** qualifying enactments occur in the trailing 8.5 months: the 2026 rows are Budapest (<1%), Thessaloniki (<1%), Amsterdam (<1%), Florence (<1%) and the EU data-sharing regulation (type gate). λ estimated over 24 months is therefore an average of an active 15-month period and a silent 9-month one, projected onto a 4.8-month window that begins in the silent period. | Counted the qualifying rows by date against `data/processed/abnb_regulatory_events.csv` and the 32-factor register extract, then recomputed: trailing **12** months = 1 event (Canary Law 6/2025, 10 Dec 2025) → λ 0.402, **P = 0.331**; trailing **18** months = 3 → λ 0.805, **P = 0.553**; trailing 24 = 6 → 0.701. | Publish the recency profile, not one number. The base-rate leg is **0.33–0.55**; 0.70 is the most favourable window available. The decomposition is the stronger of the two legs and should carry the weight — which is also why A15-12 and A15-13 matter more than they look. |
| A15-05 | B06 | major | `log:80`; `datasets/letter_geopolitical_base_rate_4Q20-2Q26.csv` row 1Q22; `forecast.estimates.base_rate_construction` | The base rate takes the most lenient of three defensible codings and reports only it. 1Q22's outlook sentence is a **risk list**, not an attribution or an assumption behind a guide, which is what the question ("a named reason for the 4Q26 guide") and convention 2 ("a factor in or assumption behind the guide") both require. 3Q23's clause names no event at all ("geopolitical conflicts" generically). | Regex over all 23 letters, verbatim: 1Q22 — "Risks to nights booked in Q2 2022 and the remainder of the year include additional COVID outbreaks, any impact to travel from the conflict in Ukraine, and consumer price sensitivity"; 3Q23 — "closely monitoring macroeconomic trends and geopolitical conflicts that may impact travel demand. We currently expect our nights booked growth in Q4 2023 to moderate"; 1Q26 — "assuming an estimated roughly 100bps headwind related to the conflict in the Middle East". | Report the bracket: strict **1/8** (Laplace 0.20), moderate **2/8** (0.30), lenient **3/8** (0.40). Use **0.30** as the base-rate route. The log's convention 2 already says the 3Q23 construction counts, so 2/8 is the coding consistent with its own rules. |
| A15-06 | B06 | major | `datasets/letter_geopolitical_base_rate_4Q20-2Q26.csv`, `active_conflict` column | The denominator is endogenous: a print enters the reference class partly because management discussed the conflict. Israel–Hamas was active through 2024 and Ukraine through 2023–2026, yet 1Q23–2Q23 and 1Q24–4Q25 are coded "none". The dataset's own 1Q24 row records the call attributing the October 2023 dislocation to Israel while coding 1Q24 `active_conflict = none`. | Read the column against the dated conflicts and against the row's own note text. On a "major war ongoing anywhere" denominator the class is ~18–23 prints and the rate is **3/18 to 3/23 = 0.13–0.17**. | State the selection rule explicitly ("a conflict management had already linked to booking trends by the print date") and report the wide class alongside. §7 already carries the 23-print alternative at 0.13; promote it into §5 so the reader sees both classes. |
| A15-07 | B04 | major | `log:100` (§7); claim 6; `research/notes/2026-09-07_fee-churn-recent-followup.md:24` | The one market with a **completed** migration is quoted on the basis that looks best. Claim 6 gives London all-ID disappearance 5.12% / 4.95% and omits the reviewed-home rates given in the same sentence of the source note — **5.63% and 6.38%** — which is the basis the §7 trigger uses ("reviewed-home disappearance ≥6% on the 13-market panel"). London's UK hosts migrated on 22 June; London is therefore already **above** the log's own +0.09 trigger, on the log's own metric, in the only completed natural experiment available. | Read the source note line and `data/processed/fee_churn_recent/pooled_rates.csv` (13-market reviewed-home Jun–Jul **3.32%**, Jul–Aug **4.20%**, which is the "4.2%" the trigger is set against). | Quote both bases for London. P(material observable churn by Jan 2027) = 0.25 is set against a null (the October 2025 PMS wave) drawn from property managers; the one individual-host migration on the record reads ~1.5x the panel on the trigger metric. Raise it to **0.35** and say why; that alone takes the decomposition to 0.22. |
| A15-08 | B04 | major | claim 13; `log:86` (anchor_estimate); `forecast.estimates.anchor_source` | The internal analogue used as the only sanity check on the level is stale by one revision, and it is quoted in the direction that supports the published number. | `rnpl-negative-effect-acknowledged/forecasts/2026-09-17-forecast.json` is at **revision 2** with `p = 0.27`, ci [0.15, 0.40]. The log quotes **0.20** from revision 1, in both §5 and the JSON's `anchor_source`. | Quote 0.27. Then note the direction it implies: C07 is **one print** with a stricter mechanism, B04 is two prints plus a 10-K plus a 10-Q with a mechanism that has a hard deadline inside the window. The analogue argues for a number above 0.27-adjusted-for-window, not below it. Keep `anchor: null` with `NO_EXTERNAL_ANCHOR` — that part is right. |
| A15-09 | B06 | major | `log:112,116,119,121`; `forecast.impact.nights_3q26_pts` | The 3Q26 row double-counts. 3Q26 is printed on 5 November, before resolution; a management statement quantifying a conflict drag *reveals* the drag, it does not create it. The memo's base case for 3Q26 is the team nowcast (+9.5%), which is estimated from realised booking activity and therefore already contains any conflict effect. B07's log gets this exactly right ("Q3 is printed before resolution; the July reading is already inside the nowcast stack"); B06's does not. | Compared `log:112–121` with B07 `log:113` and with brief rule 6. The 4Q26 revenue row (−$21M) and the FY26 margin row (−0.15pp) both inherit the 3Q26 half of the drag. | Set `nights_3q26_pts = 0`. Keep the 4Q26 guide row at −0.7 (the guide genuinely carries the assumption, as the 1Q26 Q2 guide did). 4Q26 revenue becomes −$21M on the Q4 leg alone, FY26 margin about **−0.10pp**, and the EV falls to about **−$0.35**. The immaterial verdict is unchanged. |
| A15-10 | B06 | major | `log:124`; `forecast.impact.stock_usd_per_share`, `.note` | The only evidence offered for the "reaction-softening" offset flips sign under the convention the comparison base rate uses, and the offset itself is never quantified — "−$1.0 to −$3.4 fundamental offset by the reaction-softening effect" simply becomes −$1.5. | `data/processed/abnb_earnings_reactions.csv` row **2026Q1**: `abnb_1d_pct` **+0.7**, `qqq_1d_pct` **+2.3**, `excess_1d_pct` **−1.6**. The brief's comparison base rate ("decelerating prints post-2022 −5.6% day-1 excess") is on the **excess** convention, on which the 1Q26 print was negative. | State the convention and show two lines: a fundamental debit and a reaction credit, each with its own number. On the excess convention the 1Q26 data point supports no credit at all, which makes the stock line closer to −$2.5 and the EV about −$0.9 before A15-09 — still under the bar. |
| A15-11 | B05 | major | `log:89`; `forecast.estimates.decomposition_construction` | The decomposition product is mis-evaluated. | 1 − Π(1−p) over [0.18, 0.15, 0.30, 0.12, 0.12, 0.10, 0.05, 0.10, 0.01] gives complement **0.28783** and P **0.71217**. The log states "1 − 0.273 = 0.73". | Publish **0.71**. The log then reads it down to "≈ 0.70" for correlation, so the final does not move; the stated arithmetic must still be right in a memo a judge can check in ten seconds. |
| A15-12 | B05 | major | `log:89`, claim 5; `data/processed/abnb_regulatory_events.csv` | Each route probability is an undocumented haircut on a register `p27` that measures a **different and harder** event over a **longer** window, and only the window adjustment is applied. B05 needs mere enactment of any convention-1 restriction; the register's events are far more demanding. | Read the register's `event` strings: ES-REMOVE = "takes at least **25,000 more** Airbnb ads offline"; ES-REGIONS = "remove or freeze a **measurable share** of Spanish supply"; IE-REG = "enforcement removes **more than 20%** of Irish listings within 12 months"; UK-ENG = "councils use it to remove or cap supply in **at least two large tourist areas**"; IT-NAT = "**night caps or zone bans** in Rome, Venice, Milan"; PARIS-PRO = "**quota or ban**". All `p27` values quoted in claim 5 verify exactly (0.12 / 0.35 / 0.45 / 0.30 / 0.30 / 0.70 / 0.20 / 0.35 / 0.20 / 0.30 / 0.00). | Show the two adjustments separately for each route: (a) window 4.8/15.5 months, (b) bar relaxation from the register's loss-bearing outcome to bare enactment. The second raises most routes; the log applies only the first, so the pipeline as published is neither the register's number nor a derived one. |
| A15-13 | B05 | major | convention 2 (`log:29`) vs §5 pipeline | Convention 2 states that "a measure enacted before 17 Sep whose effective date falls in the window also counts: 'take effect'", and then the pipeline prices **only new enactments**. Under the convention as written, phased implementations already on the books are live Yes routes and are never enumerated. This is the largest untested swing in the number, and it runs opposite to A15-04. | Read convention 2 against the nine-route product at `log:89` and against the register's `dates` column: Canary Law 6/2025 is "Enacted; phased implementation"; Spanish regional decrees and Italian budget provisions conventionally commence 1 January; the question's title says "**new**". | Either operationalise the convention (enumerate every already-enacted measure with an effective date between 17 Sep 2026 and 11 Feb 2027 in a ≥1% jurisdiction — worth roughly +0.15 to +0.20 on the pipeline), or narrow it to "newly enacted" as the title says and delete the "or taking effect" clause. Do not leave it stated and unused. |
| A15-14 | B05 | major | `log:136,137`; `forecast.impact.ev_stock_usd_per_share`, `.material` | The "material" flag is an artefact of the brief's P × impact rule applied to a likely event. A 0.68-probability event is already 68% in the price; the memo trades the surprise, not the level. The −1% headline drift is also hard to defend for an event class the log itself shows has never moved the stock. | Surprise EV = (1 − 0.68) × −$2.5 = **−$0.80/share**, under the $1 bar. `data/processed/abnb_big_moves_7pct.csv`: 41 moves ≥7%, drivers **macro 20, earnings 11, company 9, competitor 1, regulatory 0**. `abnb_regulatory_profile.csv` confirms claim 13's 2027 median drag 0.4499% of revenue and $2.7837/share. | Report both EVs (level −$1.70, surprise −$0.80) and take the material flag off, or keep it with the caveat the log already wrote. The log's own recommended memo treatment — one line, quote the tail — is right and should survive. |
| A15-15 | B04 | major | `log:116,129`; `forecast.impact` | The impact table conditions on a mechanism that only half the Yes probability carries. Of the decomposition's 0.18, only **0.09** is "material churn attributed to the fee"; the other 0.09 (price-increase attribution 0.04, ≤3% disclosure 0.02, 10-K risk sentence 0.03) comes with no churn at all. Booking the 5%-churn scenario against the whole 0.15 overstates the EV by roughly 2x. | Read `log:85` against `log:116`. `data/processed/fee_churn_history/catalyst_scenarios.csv` confirms the grid row used (affected 0.5, churn 0.05, recapture 0.5, take-rate 0): revenue **−1.25%**, **−$45.10M**/qtr; the 2% and 10% rows give −0.5% / −$18.04M and −2.5% / −$90.20M, all as claimed. | Weight the impact by route: E[impact \| Yes] ≈ half the churn scenario. EV ≈ **−$0.5/share**, not −$0.96. The immaterial verdict strengthens from "borderline" to clear, which is the useful conclusion for the memo. |
| A15-16 | B04 | major | `log:85` (decomposition, "+0.03 resolver counts a 10-K risk-factor sentence") | Convention risk is priced twice and in the wrong place. Convention 1 explicitly resolves a hypothetical "may" sentence **No**; adding 0.03 for the resolver ignoring that convention puts convention risk inside the point estimate, where §7 already prices the same branch at 0.30. | Compared convention 1 (`log:28`) with the decomposition's fourth term and with §7 row 1. | Remove the 0.03 from the point (decomposition 0.18 → 0.15) and leave the branch in §7. The final should move up for the reasons in A15-01 and A15-07, not down — but it should move up from a clean decomposition. |
| A15-17 | B04 | minor | claim 1 | "+17% ex quality removals" mis-describes the 1Q24 adjustment. | 1Q24 letter, verbatim: "active listings **excluding experiences** grew 17% year-over-year with sustained double-digit supply growth across all regions"; separately "Active listings grew 15% in Q1 2024 compared to a year ago". | Say "excluding experiences". The load-bearing half of claim 1 is correct and important: a regex over all 23 letters confirms **1Q24 is the last percentage disclosure** (2Q24–3Q24–4Q24 give no rate; 1Q25 "approximately in-line"; 2Q25 "slightly above"; 3Q25/4Q25/1Q26 "relatively in-line"; 4Q25 "over 9 million active listings"; **2Q26 has no "active listings" phrase at all**, only "Our supply strategy is deliberate and precise"). |
| A15-18 | B04 | minor | `log:84` | The base-rate route names three opportunities ("two prints plus a 10-K") and then exponentiates two: 1 − (1−0.04)² = 0.0784. | Arithmetic. Three gives **0.115**. | Use the number of opportunities the window actually contains, or say why the 10-K is not independent of the February print (it is filed the same week, often the same day). |
| A15-19 | B05 | minor | convention 4 (`log:31`); claim 3 | The city anchors are **GBV** shares applied against a **nights** gate. Paris ≈ 1.0% of global GBV ÷ 0.40 = 2.5% of EMEA *GBV*; Paris ADR runs well above the EMEA average, so Paris is nearer **1.6–1.8%** of EMEA nights, London ~1.4%, and **Rome falls to about 1.05–1.1%** — on the line rather than comfortably over it. | `data/processed/overnight/10_regional_panel_quarterly.csv` 2Q26: `emea_nights_share_est_pct` **39.6**, `emea_revenue_share_pct` **39.50** (so the regional GBV/nights conversion is ~1:1, but the within-region city conversion is not). Register anchors verify: Paris 1.0% of global GBV, London 0.8%, Rome 0.6%, Ireland 0.4% of global revenue. | Say the gate is applied on GBV and name Rome as borderline. Nothing in the decomposition turns on it — the Italy route is a **national** measure and Italy is 11.7% of EMEA — but a judge will ask. |
| A15-20 | B05 | minor | claim 2; `datasets/eurostat_country_shares_scaled_to_emea.csv` | Eurostat's series is **four-platform** nights (Airbnb, Booking, Expedia, TripAdvisor), not Airbnb nights, and Airbnb's European country mix differs from Booking's — France is Airbnb-heavy, Croatia/Greece/Italy are Booking-heavy. The ×0.8 EU27→EMEA scaler is asserted with no derivation. | Recomputed the shares from the saved table; the RESUME already flags the scaler. **It is independently corroborated**: the register's ES-REMOVE anchor derives "Spain about 6% of global revenue (20% of EU platform nights × ~30% EU share of revenue)", which puts Spain at ~15% of EMEA against the scaled table's **15.93%**. | Publish that cross-check — it is the strongest support the gate has. Then flag the platform-mix bias as a reason the borderline rows (AT 2.09%, NL 1.00%) are not reliable to the second decimal. |
| A15-21 | B05 | minor | `datasets/qualifying_events_trailing_24m.csv` | The trailing-24-month table may be one event short, and the missing candidate is the only 2026 one that could clear the gate. The register's own IT-NAT `gates` field says "national **2026 budget law raised the business threshold**" — an Italy-wide (11.7% of EMEA) restriction on multi-property hosting, enacted late 2025 and effective January 2026 — and it is not in the table. | Read `data/processed/abnb_regulatory_events.csv` row IT-NAT against the 15 rows of the trailing-24m table. | Add it with a `qualifies` verdict either way. It is the difference between **0 and 1** qualifying enactments in the trailing 12 months, which is exactly the quantity A15-04 turns on. |
| A15-22 | B05 | minor | `log:131`; `forecast.impact.rev_fy27_musd` | "−25 (0.15% of ~$15.6bn, **half-year weighting** on the run-rate mode)" is the full-year figure. 0.15% × 15,600 = **$23.4M**; half-year weighted it is **$11.7M**. | Arithmetic. The downstream rows (margin −0.10pp, EPS −$0.02) are consistent with −$25M, so the error is in the description, not the chain. | Delete "half-year weighting" or halve the row. Immaterial to the verdict; it is the kind of line a judge reads aloud. |
| A15-23 | B06 | minor | `log:121`; `forecast.impact.margin_fy26_pp` | −0.15pp does not follow from its own stated formula. "0.7pt × 0.59pp × ¼ FY weight" = **−0.103**; a two-quarter weight gives **−0.207**; neither is −0.15. | Arithmetic against brief §Sensitivities ("2H26 0.59pp held / 0.38pp flex"). | State the weight. After A15-09 removes the 3Q26 leg the right figure is about **−0.10pp** on held costs, −0.07 on flex. |
| A15-24 | B07 | minor | `log:121`; `forecast.impact.stock_usd_per_share` | 0.06pt of FY27 nights × $4.90 = **$0.29**, booked as −$0.2. | Arithmetic against brief §Sensitivities. | Use −$0.3, or say "rounded down". The EV moves from −$0.12 to −$0.17; the immaterial verdict is untouched. |
| A15-25 | B04, B05, B06, B07 | minor | each `sources/` | The "nothing new / no measured figure" claims (B04 claim 15, B05 claim 15, B06 claim 14, B07 claim 14) are stated as facts about the world but rest on WebSearch snippets with no saved result payloads — the same gap flagged as A11-24. | Inventoried all four `sources/` directories: they hold the Polymarket JSON, markdown search notes, the letter/transcript extractions and B07's saved HTML — no search result payloads, and three fetches (CNBC, CRS, Travel Weekly) returned 403 and are noted as such. | Write "no relevant result in the searches recorded". **B07 is the exception and is the model**: `i94_arrivals_program_page_2026-09-17.html` is saved at HTTP 200 and independently supports claim 6 (latest Preliminary = **July 2026**, latest Final = **June 2026**, no August file, and the page's own 8th/18th/28th Advance/Preliminary/Final cadence, which also validates the monitoring dates). |

## B04 — what the log does well and should keep

The conventions are the sharpest thing in the batch. Separating an **observed-effect** attribution from a hypothetical risk-factor sentence, ruling that "hosts absorbed the fee" is the opposite sign and resolves No, and ruling that "grew relatively in line with Nights and Seats Booked" resolves No while nights grow above 3% are three decisions the question genuinely needs, all written down before the modelling. Keep them verbatim.

The letter archaeology is correct and is the strongest evidence in the log. A regex over all 23 letters confirms every step of claim 1: the last percentage disclosure of active-listings growth is **1Q24** ("Active listings grew 15% in Q1 2024"; "excluding experiences grew 17%"), every letter from 1Q25 gives a relative phrase instead, 4Q25 gives a level ("over 9 million active listings around the world"), and the **2Q26 letter contains no "active listings" phrase at all**. Claim 2's "form for dropping metrics that stop flattering" is the right behavioural model and this is a clean instance of it. Leg 2 really is nearly dead, and the log is right to price it at 0.02.

The 10-K work checks out. `abnb_2025_10k.json` describes the transition neutrally in the revenue-recognition note ("In October 2025, the Company began transitioning to a single-fee structure, charging only the host a service fee"), contains no host-attrition sentence tied to the fee, and gives no active-listings growth figure — only "no single city represented more than … 1% of our active listings". Claim 4 is accurate as written.

Every management quote in claim 3 verifies verbatim against the transcript mirrors: Mertz's 4Q25 "many of the hosts did not take up their rates. Instead, the effective ADR to guests came down modestly"; the 2Q26 "helped our host price more competitively … Approximately half of our active listings are now subject to the single service fee"; Chesky's "we haven't really gotten much feedback from our core hosts." That three-call record of denial is the real argument for a low number and should be the headline of the No case — it is stronger than the false 0/23 base rate it currently sits behind.

The strongest case against 0.15 is the one the log does not make: the RNPL episode shows exactly how Airbnb answers this kind of question, and the answer form ("yes, there is a negative; the net is positive") resolves **Yes** under convention 1.

## B05 — what the log does well and should keep

Convention 1 is a genuine resolution rule a judge could apply: a binding cap, ban, zone ban, moratorium, licence non-renewal, registration-with-removal or principal-residence requirement counts; taxes, data sharing, safety standards and platform fines do not. It correctly disposes of the two 2026 events that would otherwise look like resolutions (the EU data-sharing regulation, the Greek operating standards) and it is stated before the modelling.

The market-size work is real, sourced and internally cross-checked. Every Inside Airbnb count in claim 3 is in `regulatory_market_inventory.csv`; every Eurostat share in claim 2 is in the scaled table; every register `p27` in claim 5 and every conditional loss in claim 13 verifies exactly against `abnb_regulatory_events.csv`; and the ×0.8 scaler is independently corroborated by the register's own revenue-route estimate for Spain (15.9% vs ~15%). That is more source discipline than the question needed.

The web notes are the best in the batch: dated, URL-stamped, and honest about conflicts (the Spanish judgment dated 21 May in one source and 19 May in the register; the Thessaloniki freeze at 1 March in GTP and 1 July in the register). The Greek finding — Law 5313/2026 replaced the hard end date with extension "by a future joint ministerial decision", and "no official 2027 extension decision has been published" as of 13 Aug 2026 — is the kind of specific, checkable, calendar-anchored fact the monitoring table can act on.

The impact section reaches the right conclusion by the right route and should go into the memo almost verbatim: 0 of 41 moves ≥7% since 2020 were regulatory, the 2027 median drag is 0.45% of revenue, and the honest summary is "likely, not large". The §7 lenient/strict gate row (0.40 / 0.85) is the correct way to carry a convention that decides the question.

## B06 — what the log does well and should keep

Convention 3 is the best judgement call in the batch. Ruling that a **negation** — "In Q3, we are not assuming any significant impact related to the conflict in the Middle East" — names the conflict but attributes no headwind and resolves **No** is exactly right, it is the modal wording if the conflict is live, and pricing it at 0.05 as an explicit resolver risk is the honest treatment. The quote verifies verbatim in the 2Q26 call, inside the prepared Q3 outlook remarks.

The letter sweep is complete and accurate. I reproduced `letter_geopolitical_base_rate_4Q20-2Q26.csv` row for row from all 23 letters, and every coding decision in the file is defensible on its face: 2Q22's "despite the continued war in Ukraine" is a results sentence, 3Q22's "despite geopolitical and macroeconomic headwinds" is a headline, 4Q22 mentions Ukraine only as an easier comparison, 4Q23 does not mention it at all. The two exceptions are 1Q22 and the `active_conflict` column (A15-05, A15-06); everything else stands.

Claim 9 is the observation that should survive into the memo: "the largest airfare shock since 2022 coincided with the fastest nights growth in two years", and Airbnb's nights have absorbed every macro and geopolitical shock since 2022 inside a 7–12% band. The risk is in the wording, not the KPI. That is the correct frame for a question about language.

The Polymarket use is disciplined. The snapshots contain the quoted prices, and the log explicitly refuses to call them an anchor — they establish P(the conflict is live on 5 Nov) ≈ 0.85–0.90, which is an input, not a price on management's language. Keep `NO_EXTERNAL_ANCHOR`.

The §9 note's closing judgement is the most valuable sentence in the batch and should go to the memo unchanged: a named, quantified external cause is **worse for the short than for the long**, because it turns "deceleration" into "one-off". Listing B06 under risks to the short's narrative rather than under bonus items is the right call.

## B07 — what the log does well and should keep

The data work is clean and complete. Every figure in claims 1 through 5 reproduces from `data/processed/q3nowcast/G/raw/ntto_arrivals_monthly.csv` — the monthly y/y series, the quarterly sums, the two-year stacks, all nine regional shares and their July and 2Q26 y/y rates, and the full 18-row persistence table to **zero** maximum absolute difference. That is the standard the other three logs should be held to.

The cache is externally validated, and the log has the evidence in its own sources without saying so. The saved search notes carry four independent published figures, and the cache reproduces all four: January 2026 overseas **−4.2%** (cache −4.21), first five months of 2026 **−4.8%** (cache −4.78), 2025 total international **−5.5%** (cache −5.55), and the 2025 overseas level **34.3m** (cache 34.29m). That answers the RESUME's own open question — the OVERSEAS region in the team cache *is* NTTO's published Overseas total — and it should be written into the log as a validation rather than left implicit.

Claim 10 is handled exactly right: the Tourism Economics / Brand USA forecast is on a different definition (42.6m vs the I-94 COR series' 34.3m), is inconsistent with the realised −4.7% year to date, and is given **zero weight as a level anchor** while its sign is noted. Refusing a convenient external number because its denominator is wrong is the right instinct and is rare.

Claim 9 kills the World Cup confound in one line (a June–July event; the 2027 comparison problem is 2Q27/3Q27), and claim 12 is the reason the whole question is immaterial and should be the only thing the memo keeps: inbound is 2–3% of Airbnb's business, and BEA inbound spending ran −4.8% to −8.6% for five straight quarters while North American nights **accelerated**. The materiality verdict is right, the impact table needs no rework, and the recommendation to drop the number and keep one clause is correct.

The monitoring calendar is the most actionable in the batch and matches the publication cadence on the saved trade.gov page: August preliminary ~10 October, September ~10 November (completes Q3), October ~10 December (the first Q4 month), December ~10 February. The "each 1pp on Q3 moves P by about 0.08" rule is the right kind of pre-registered update.

## Independent audit numbers

These are audit judgements built from the same repository inputs, not blinded second forecasts. No tradable market exists for any of the four questions; I confirmed that against the saved Polymarket snapshots rather than refreshing them.

**B04: P(Yes) = 0.24.** Judgmental 80% interval **0.14–0.38**.
Four routes, on corrected inputs. An attribution at the 5 Nov print **0.06** (the migration is only 62% complete in 3Q26 per `03_migrated_share_path.csv`, so the quarter carries almost no post-deadline data); at the February print, call or FY26 10-K **0.16** (4Q26 is 94% migrated, the deadlines fall inside the quarter, Morgan Stanley's supply thesis makes an analyst question near-certain, and D006 is the template for how that question gets answered); leg 2 at ≤3% **0.02**; a non-hypothetical 10-K MD&A sentence **0.03**. Union = 1 − 0.94 × 0.84 × 0.98 × 0.97 = **0.249**.
The corrected base rate agrees: 2 of 23 prints carry a self-product negative attribution (Laplace 0.12/print → 0.226 over two prints), against 0 of 3 for the fee specifically, which is the reason to sit at the bottom of that range rather than above it. Impact: E[impact \| Yes] ≈ half the churn scenario, so stock ≈ **−$3.2** and EV ≈ **−$0.77** — immaterial, cleanly rather than borderline.

**B05: P(Yes) = 0.62.** Judgmental 80% interval **0.42–0.80**.
Rebuilt pipeline over the 4.83-month window, at the question's bar (enactment, not the register's loss outcome): Spain regional 0.28, Spain national replacement registry 0.12, Greece gated 0.18, Paris 0.08, Italy (the 2027 budget law is enacted in late December and commences 1 January, squarely inside the window) 0.12, England 0.07, Portugal 0.04, another ≥1% market not in the register 0.10, EU act 0.01 → union **0.665**; adding the convention-2 "already enacted, takes effect in the window" route at 0.20 gives **0.732**; a correlation haircut for one shared European housing-politics factor (register rho 0.45) takes it to about **0.67**.
Blended against the recency-honest base rate (0.33 on 12 months, 0.55 on 18) rather than the 24-month 0.70, the answer is **0.62**. The published 0.68 is inside my interval; it is the base-rate leg, not the headline, that should change. Materiality: surprise EV **−$0.80**, under the bar.

**B06: P(Yes) = 0.33.** Judgmental 80% interval **0.20–0.47**.
Leg 2 first, because it carries the question: P(conflict live and salient on 5 Nov) **0.85** (Polymarket-informed, claim 12) × P(the Q4 outlook paragraph or the CFO's prepared Q4 remarks mention it at all) **0.70** (both Iran-war prints did, 1Q26 as an assumption and 2Q26 as a negation) × P(it reads as an assumed headwind rather than a negation) **0.45** (the September re-escalation and Gulf suspensions into late October argue up; "less than we had anticipated" and the EMEA recovery argue down) = **0.268**. Add a standalone quantified 3Q26 drag on the 1Q26 template at **0.07** incremental (the quarter is mostly clean — the 28 August resumption leaves about one month inside 3Q26) and another geopolitical event at **0.02**. Union = **0.333**.
The corrected base rate brackets it: 2 of 8 active-conflict prints on the coding consistent with the log's own convention 2, Laplace **0.30**. Impact after A15-09 and A15-10: stock about **−$2.0**, EV about **−$0.7** — immaterial, and still the wrong sign for a short.

**B07: P(Yes) = 0.63.** Judgmental 80% interval **0.47–0.77**.
Centre the 4Q26 y/y at **−6.8%**, the midpoint of three routes I recomputed from the cache: aggregate constant-July-stack **−7.53%**, regional constant-stack on nine regions at 4Q25 weights **−7.08%**, and the 4Q25-share-weighted July y/y **−6.83%**. The persistence class is the better-behaved estimator (the Q4−Q3 delta has sd 4.04 over 18 years, against 7.16 for a naive constant-stack backtest over 17), so use its dispersion, widened to **4.2** for the unknown August and September.
P(≤ −5%) = Φ((−5 + 6.8)/4.2) = **0.665**; on the persistence route alone with a stack-consistent Q3 of −5.75% it is 0.621. Call it **0.63**. Note that the two-year-stack framework already embeds the October 2025 visa/ESTA lapping — claim 8 should not be credited a second time in the mean-reversion pull, which is where the base-rate route's fourth branch (0.50) comes from.

## Reproduction script

Read-only, stdlib plus pandas, no numpy or scipy, no network, no file writes. Run from the repository root with `python -B docs/pitch-forecasts/audits/A15-reproduce.py`. It recomputes every base rate and arithmetic check asserted above and prints the saved-versus-recomputed comparison for the two datasets that can be regenerated from repository sources.

```python
"""A15 read-only reproduction (B04, B05, B06, B07).
Run from the repository root: python -B docs/pitch-forecasts/audits/A15-reproduce.py
Requires stdlib + pandas only (no numpy/scipy). Writes nothing; no network.
"""
from pathlib import Path
from statistics import NormalDist
import glob
import html
import json
import math
import os
import re

import pandas as pd

ROOT = Path.cwd()
Q = ROOT / "docs/pitch-forecasts/questions"
N = NormalDist()


def head(t):
    print("\n" + "=" * 12 + " " + t + " " + "=" * 12)


def pct(a, b):
    return 100.0 * (a / b - 1.0)


# ------------------------------------------------------------------ B07
head("B07 NTTO overseas: the cache and the claims ledger")

raw = pd.read_csv(ROOT / "data/processed/q3nowcast/G/raw/ntto_arrivals_monthly.csv")
raw["p"] = pd.PeriodIndex(raw.month, freq="M")
S = raw[raw.region == "OVERSEAS"].set_index("p").arrivals.sort_index()


def P(s):
    return pd.Period(s, "M")


def qsum(series, year, q):
    m = {1: 1, 2: 4, 3: 7, 4: 10}[q]
    return series[P(f"{year}-{m:02d}"):P(f"{year}-{m + 2:02d}")].sum()


yoy = (S / S.shift(12) - 1) * 100
print("2026 monthly y/y:", {str(k): round(v, 2)
                            for k, v in yoy[yoy.index >= P("2026-01")].items()})
print("2025 monthly y/y:", {str(k): round(v, 2)
                            for k, v in yoy[(yoy.index >= P("2025-07")) &
                                            (yoy.index <= P("2025-12"))].items()})
print("  -> Sep 2025 is the WEAKEST month of 3Q25, i.e. the easiest 3Q26 comp")

for lab, y, q in [("3Q25", 2025, 3), ("4Q25", 2025, 4),
                  ("1Q26", 2026, 1), ("2Q26", 2026, 2)]:
    yy, qq = (y, q) if q else (y, q)
    print(lab, "y/y %:", round(pct(qsum(S, yy, qq), qsum(S, yy - 1, qq)), 3))

print("4Q25 two-year stack %:", round(pct(qsum(S, 2025, 4), qsum(S, 2023, 4)), 3),
      "| 4Q24 y/y %:", round(pct(qsum(S, 2024, 4), qsum(S, 2023, 4)), 3))
ytd = S[P("2026-01"):P("2026-07")].sum(), S[P("2025-01"):P("2025-07")].sum()
print("Jan-Jul 2026 vs 2025 (m):", round(ytd[0] / 1e6, 3), round(ytd[1] / 1e6, 3),
      "y/y %:", round(pct(*ytd), 3))
stack = (S / S.shift(24) - 1) * 100
print("2026 two-year stacks:", {str(k): round(v, 2)
                                for k, v in stack[stack.index >= P("2026-01")].items()})

# External cross-validation of the cache (figures quoted in the saved search notes)
print("cache vs published: Jan 2026", round(yoy[P("2026-01")], 2), "(pub -4.2)")
print("cache vs published: Jan-May 2026",
      round(pct(S[P("2026-01"):P("2026-05")].sum(),
                S[P("2025-01"):P("2025-05")].sum()), 2), "(pub -4.8)")
print("cache vs published: FY2025 overseas level (m)",
      round(S[P("2025-01"):P("2025-12")].sum() / 1e6, 2), "(pub 34.3)")
tot = raw[raw.region == "TOTAL ALL COUNTRIES"].set_index("p").arrivals.sort_index()
print("cache vs published: FY2025 total international y/y %",
      round(pct(tot[P("2025-01"):P("2025-12")].sum(),
                tot[P("2024-01"):P("2024-12")].sum()), 2), "(pub -5.5)")

head("B07 persistence table (claim 5) and the saved dataset")
rows = []
for y in list(range(2004, 2020)) + [2024, 2025]:
    q2 = pct(qsum(S, y, 2), qsum(S, y - 1, 2))
    q3 = pct(qsum(S, y, 3), qsum(S, y - 1, 3))
    q4 = pct(qsum(S, y, 4), qsum(S, y - 1, 4))
    jul = pct(S[P(f"{y}-07")], S[P(f"{y - 1}-07")])
    rows.append(dict(year=y, q2=q2, jul=jul, q3=q3, q4=q4,
                     d_q4_jul=q4 - jul, d_q4_q2=q4 - q2, d_q4_q3=q4 - q3))
mine = pd.DataFrame(rows).round(2).set_index("year")
saved = pd.read_csv(Q / "bonus-us-inbound-falls/datasets/ntto_q4_persistence.csv"
                    ).set_index("year")
print("max abs diff vs saved dataset:",
      (mine - saved[mine.columns]).abs().max().max())
for c in ["d_q4_q3", "d_q4_jul", "d_q4_q2"]:
    s = mine[c]
    print(c, "n", len(s), "mean", round(s.mean(), 2), "sd", round(s.std(ddof=1), 2),
          "MAD", round((s - s.median()).abs().median(), 2))

head("B07 recomputed centres and probabilities")
st26 = S[P("2026-07")] / S[P("2024-07")] - 1
q3_hold = (S[P("2026-07")] + S[P("2024-08")] * (1 + st26) +
           S[P("2024-09")] * (1 + st26))
q3_hold = pct(q3_hold, qsum(S, 2025, 3))
q4_hold = pct(qsum(S, 2024, 4) * (1 + st26), qsum(S, 2025, 4))
print("July 2026 stack %:", round(100 * st26, 2))
print("3Q26 at a held stack %:", round(q3_hold, 2),
      "(log uses -6.5, which needs a stack of about -11.0)")
print("4Q26 at a held stack %:", round(q4_hold, 2), "(log's persist scenario: -5.6)")

REG = ["WESTERN EUROPE", "ASIA", "SOUTH AMERICA", "CENTRAL AMERICA", "CARIBBEAN",
       "OCEANIA", "EASTERN EUROPE", "MIDDLE EAST", "AFRICA"]
piv = raw.pivot_table(index="p", columns="region", values="arrivals")
w4 = piv.loc[P("2025-10"):P("2025-12"), REG].sum()
print("4Q25 regional shares %:",
      {k: round(v, 2) for k, v in (100 * w4 / w4.sum()).items()})
jul_yoy = (piv.loc[P("2026-07"), REG] / piv.loc[P("2025-07"), REG] - 1) * 100
print("Jul 2026 regional y/y %:", {k: round(v, 2) for k, v in jul_yoy.items()})
print("4Q25-share-weighted Jul y/y %:",
      round(((w4 / w4.sum()) * jul_yoy).sum(), 2))
rs = piv.loc[P("2026-07"), REG] / piv.loc[P("2024-07"), REG]
q4r = (piv.loc[P("2024-10"):P("2024-12"), REG].sum() * rs).sum()
print("regional constant-stack 4Q26 y/y %:",
      round(pct(q4r, piv.loc[P("2025-10"):P("2025-12"), REG].sum().sum()), 2))

print("log base-rate branches:",
      [round(N.cdf((-5 + 7.0) / s), 4) for s in (4.0, 3.6)],
      round(N.cdf((-5 + 8.0) / 5.0), 4), round(N.cdf((-5 + 5.0) / 4.0), 4))
mix = sum(w * N.cdf((-5 - mu) / 2.0)
          for w, mu in [(0.55, -5.6), (0.30, -3.5), (0.15, -8.2)])
print("log decomposition mixture:", round(mix, 4))
for mu, sd in [(-6.24, 4.04), (-6.8, 4.2), (-7.08, 4.2), (-7.53, 4.2)]:
    print(f"  auditor centre {mu} sd {sd} -> P(<=-5) {N.cdf((-5 - mu) / sd):.3f}")

# ------------------------------------------------------------------ B06
head("B06 geopolitical base rate: dataset, letters, reaction")
g = pd.read_csv(Q / "bonus-geopolitical-headwind-cited/datasets/"
                    "letter_geopolitical_base_rate_4Q20-2Q26.csv")
active = g[g.active_conflict.str.lower() != "none"]
active = active[~active.active_conflict.str.contains("none named|tariffs", case=False)]
yes = g[g.resolves_yes_under_B06.str.startswith(("named", "quantified"))]
print("prints:", len(g), "| active-conflict prints:", len(active),
      "| coded Yes:", list(yes["print"]))
print("log coding 3/8 -> Laplace", round(4 / 10, 3),
      "| strict 1/8 (1Q26 only) ->", round(2 / 10, 3),
      "| convention-2 coding 2/8 (3Q23,1Q26) ->", round(3 / 10, 3),
      "| unconditional 3/23 ->", round(3 / 23, 3))

pat = re.compile(r"Ukraine|Middle East|geopolit|conflict", re.I)
found = {}
for f in sorted(glob.glob(str(ROOT / "data/raw/letters/*.htm"))):
    q = os.path.basename(f)[:4]
    t = re.sub(r"\s+", " ", html.unescape(
        re.sub(r"<[^>]+>", " ", open(f, encoding="utf-8", errors="ignore").read())))
    found[q] = len(pat.findall(t))
    for key in ["Risks to nights booked in Q2 2022",
                "closely monitoring macroeconomic trends and geopolitical conflicts",
                "roughly 100bps headwind related to the conflict"]:
        if key in t:
            i = t.index(key)
            print(f"  {q}: ...{t[i:i + 150]}...")
print("letters with any geopolitical hit:",
      {k: v for k, v in found.items() if v})

r = pd.read_csv(ROOT / "data/processed/abnb_earnings_reactions.csv")
r1 = r[r.quarter == "2026Q1"].iloc[0]
print("1Q26 print: raw 1d", r1.abnb_1d_pct, "| QQQ 1d", r1.qqq_1d_pct,
      "| EXCESS 1d", r1.excess_1d_pct, "<- sign flips on the excess convention")

print("B06 decomposition replay:", round(0.30 * 0.75 + 0.70 * 0.15, 4))
print("B06 FY26 margin row: 0.7*0.59*0.25 =", round(0.7 * 0.59 * 0.25, 3),
      "| two-quarter weight =", round(0.7 * 0.59 * 0.5, 3), "| log prints -0.15")
print("B06 EV:", round(0.35 * -1.5, 3))

# ------------------------------------------------------------------ B05
head("B05 regulation: gate, event count, decomposition")
ev = pd.read_csv(Q / "bonus-eu-regulation-hit/datasets/qualifying_events_trailing_24m.csv")
ev["year"] = ev.date.str.extract(r"(\d{4})").astype(int)
qual = ev[ev.qualifies_under_B05_convention.str.startswith(("yes", "marginal"))]
print("rows:", len(ev), "| qualifying (clear+marginal):", len(qual))
print(qual[["measure", "date", "qualifies_under_B05_convention"]].to_string(index=False))
print("events by calendar year:", ev.groupby("year").size().to_dict())
print("qualifying by year:", qual.groupby("year").size().to_dict(),
      "<- none dated 2026")

win = 147 / (365.25 / 12)
print("window months:", round(win, 4))
for lab, n, months in [("24m, 6 events (log)", 6, 24), ("24m, strict 4", 4, 24),
                       ("24m, lenient 13", 13, 24),
                       ("trailing 18m, 3 events", 3, 18),
                       ("trailing 12m, 1 event", 1, 12)]:
    lam = n * win / months
    print(f"  {lab}: lambda {lam:.3f} -> P(>=1) {1 - math.exp(-lam):.3f}")

routes = [0.18, 0.15, 0.30, 0.12, 0.12, 0.10, 0.05, 0.10, 0.01]
comp = 1.0
for p in routes:
    comp *= (1 - p)
print("decomposition complement:", round(comp, 5), "-> P", round(1 - comp, 5),
      "| log states complement 0.273 -> 0.73")

reg = pd.read_csv(ROOT / "data/processed/abnb_regulatory_events.csv").set_index("id")
claim5 = {"EU-AHA": 0.12, "ES-REMOVE": 0.35, "ES-REGIONS": 0.45, "PARIS-PRO": 0.30,
          "IT-NAT": 0.30, "GR-FREEZE": 0.70, "UK-ENG": 0.20, "IE-REG": 0.35,
          "PT-RETIGHT": 0.20, "NL-AMS": 0.30, "BCN-2028": 0.00}
print("claim 5 p27 check:",
      all(abs(reg.loc[k, "p27"] - v) < 1e-9 for k, v in claim5.items()))
print("register event bars (B05 needs mere enactment):")
for k in ["ES-REMOVE", "IE-REG", "UK-ENG", "IT-NAT"]:
    print("   ", k, "->", reg.loc[k, "event"][:95])
print("IT-NAT gates mention the 2026 budget law:",
      "budget law" in str(reg.loc["IT-NAT", "gates"]).lower(),
      "| present in the trailing-24m table:",
      ev.measure.str.contains("budget", case=False).any())

sc = pd.read_csv(Q / "bonus-eu-regulation-hit/datasets/"
                     "eurostat_country_shares_scaled_to_emea.csv").set_index("geo")
print("EMEA shares (scaled): FR ES IT DE EL PT PL HR AT NL IE =",
      [round(float(sc.loc[c, "emea_share_est_pct"]), 2)
       for c in ["FR", "ES", "IT", "DE", "EL", "PT", "PL", "HR", "AT", "NL", "IE"]])
inv = pd.read_csv(Q / "bonus-eu-regulation-hit/datasets/"
                      "regulatory_market_inventory.csv").set_index("market")
for m in ["Paris", "London", "Madrid", "Athens", "Barcelona",
          "Lisbon municipality", "Florence", "Amsterdam"]:
    print("  listings", m, int(inv.loc[m, "total"]))
print("Canaries / Spain INE:",
      round(100 * inv.loc["Canary Islands (INE)", "total"] /
            inv.loc["Spain (INE)", "total"], 2), "%")

panel = pd.read_csv(ROOT / "data/processed/overnight/10_regional_panel_quarterly.csv")
p2 = panel[panel.quarter == "2Q26"].iloc[0]
print("2Q26 EMEA nights share %:", p2.emea_nights_share_est_pct,
      "| EMEA revenue share %:", round(p2.emea_revenue_share_pct, 2))
print("gate is GBV-based: Paris 1.0/0.40 =", round(1.0 / 0.40, 2),
      "% of EMEA GBV; at a 1.4-1.5x city ADR premium that is",
      round(2.5 / 1.45, 2), "% of EMEA NIGHTS; Rome 1.5/1.45 =",
      round(1.5 / 1.45, 2), "% -> borderline")

big = pd.read_csv(ROOT / "data/processed/abnb_big_moves_7pct.csv")
print("moves >=7%:", len(big), big.driver.value_counts().to_dict())
prof = pd.read_csv(ROOT / "data/processed/abnb_regulatory_profile.csv")
med = prof[prof.percentile.astype(str) == "50"].iloc[0]
print("2027 median regulatory drag % of revenue:", round(med.revenue_loss_pct, 4),
      "| $/share:", round(med.value_per_share_usd, 4))
print("B05 EV level:", round(0.68 * -2.5, 3),
      "| EV on the surprise (1-P):", round((1 - 0.68) * -2.5, 3))

# ------------------------------------------------------------------ B04
head("B04 host churn: listings disclosure, RNPL precedent, churn panel")
apat = re.compile(r"active listings[^.]{0,200}", re.I)
for f in sorted(glob.glob(str(ROOT / "data/raw/letters/*.htm")),
                key=lambda f: (os.path.basename(f)[2:4], os.path.basename(f)[:2])):
    q = os.path.basename(f)[:4]
    if q[2:] < "23":
        continue
    t = re.sub(r"\s+", " ", html.unescape(
        re.sub(r"<[^>]+>", " ", open(f, encoding="utf-8", errors="ignore").read())))
    hits = [m.group(0) for m in apat.finditer(t)
            if re.search(r"\bgrew\b|\bgrowth\b|\bin-?line\b|million", m.group(0), re.I)
            and "expectations regarding" not in m.group(0)]
    print(q, "->", (hits[0][:110] if hits else "NO growth/level sentence"))

led = pd.read_csv(ROOT / "data/processed/overnight2/D/rnpl_statement_ledger.csv")
for sid in ["D006", "D009", "D017", "D018"]:
    row = led[led.statement_id == sid].iloc[0]
    print(sid, row.date, row.speaker, "|", str(row.quote)[:150])
print("-> 'management has never attributed a negative to its own product (0/23)' "
      "is false; at least 2 prints (3Q25, 4Q25) do, and 4Q25 quantifies it")

pool = pd.read_csv(ROOT / "data/processed/fee_churn_recent/pooled_rates.csv")
rev = pool[pool.cohort == "reviewed_str_homes"]
print("13-market reviewed-home disappearance:",
      [round(100 * x, 2) for x in rev.disappearance_rate],
      "(the >=6% trigger is set against the 4.20 reading)")
note = (ROOT / "research/notes/2026-09-07_fee-churn-recent-followup.md"
        ).read_text(encoding="utf-8", errors="ignore")
i = note.find("reviewed-home rates are")
snip = note[max(0, i - 190):i + 60].replace("\n", " ")
print("London (migrated 22 Jun):",
      snip.encode("ascii", "replace").decode("ascii"))

mig = pd.read_csv(ROOT / "data/processed/forecast_methods/fee_takerate/"
                         "03_migrated_share_path.csv").set_index("quarter")
print("migrated listing share: 3Q26", mig.loc["2026Q3", "listing_share_central"],
      "| 4Q26", mig.loc["2026Q4", "listing_share_central"])
sc4 = pd.read_csv(ROOT / "data/processed/fee_churn_history/catalyst_scenarios.csv")
m = sc4[(sc4.affected_booking_share == 0.5) & (sc4.demand_recapture == 0.5) &
        (sc4.relative_take_rate_change == 0)]
print("scenario grid (50% exposure, 50% recapture, no take-rate offset):",
      [(r.incremental_churn, round(100 * r.revenue_change, 2),
        round(r.revenue_change_usd_m, 1)) for r in m.itertuples()])

print("B04 base rate as written:", round(1 - 0.96 ** 2, 4),
      "| with 3 opportunities:", round(1 - 0.96 ** 3, 4),
      "| at 2/23 (Laplace 3/25) over 2 prints:", round(1 - (1 - 3 / 25) ** 2, 4))
print("B04 decomposition replay:", round(0.25 * 0.35 + 0.04 + 0.02 + 0.03, 4),
      "| without the convention-1 branch:", round(0.25 * 0.35 + 0.04 + 0.02, 4),
      "| with P(churn)=0.35:", round(0.35 * 0.35 + 0.04 + 0.02, 4))
print("B04 EV as booked:", round(0.15 * -6.4, 3),
      "| conditioned on the churn-bearing half:", round(0.15 * -3.2, 3))

# ------------------------------------------------------------------ coherence
head("Cross-question coherence and JSON checks")
for slug in ["bonus-host-churn-cited", "bonus-eu-regulation-hit",
             "bonus-geopolitical-headwind-cited", "bonus-us-inbound-falls",
             "q4-nights-bucket", "rnpl-negative-effect-acknowledged",
             "bonus-moderation-language",
             "risk-single-fee-take-rate-accretion-stated"]:
    d = json.loads((Q / slug / "forecasts/2026-09-17-forecast.json"
                    ).read_text(encoding="utf-8"))
    f = d["final"]
    if "p" in f:
        print(d["question_id"], slug, "rev", d["revision"], "p", f["p"], f["ci"])
    else:
        v = f["vector"]
        print(d["question_id"], slug, "rev", d["revision"],
              "sum", round(sum(v.values()), 6),
              "| P(bucket <= high single digits) =",
              round(sum(x for k, x in v.items()
                        if k.startswith(("(c)", "(d)"))), 4))
print("B04 quotes C07 at 0.20; C07 revision 2 is 0.27 -> stale analogue")
```
