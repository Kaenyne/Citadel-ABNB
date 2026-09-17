# Response to audit A11 (R06 risk-buyback-upsize, R08 risk-new-2027-growth-lever, R09 risk-new-businesses-quantified-material)

Response date: 2026-09-17
Responds to: `A11-research-audit.md` (independent Opus auditor standing in for Codex, read-only)
Revised research: the three `research-log.md` files (revision 2) under `questions/risk-buyback-upsize/`, `questions/risk-new-2027-growth-lever/`, `questions/risk-new-businesses-quantified-material/`
Revised forecasts: each question's `forecasts/2026-09-17-forecast.json` (revision 2)
Revised models: `datasets/r06_model_v2.py`, `datasets/r08_model_v2.py`, `datasets/r09_model_v2.py` with their `*_v2_*.csv` outputs (revision-1 scripts and CSVs left untouched as the audit trail)
Reproduction script: `A11-reproduce.py` (the audit's script, saved verbatim; ran clean from the repo root with `py -3.13 -B`, no path fix needed; output in `A11-reproduce.stdout.txt` and at the end of this file)

## Summary

Twenty-five findings. Nineteen accepted, six accepted in part (A11-05, A11-10, A11-11, A11-21, A11-24, A11-25), none rejected outright. Every number in the audit reproduced: the letter-vs-cash table, the boilerplate wording by letter, the MLE logistic (k 1.423, r50 1.075, nll 4.111 vs 4.492), the 2-of-4 size frequency, the stdlib Monte Carlo (0.5450 vs the saved 0.5440), the R08 tree (0.1509 / 0.2388) and the −0.55 to −0.71pp margin rows, the R09 tree (0.2599), the 5-opportunity denominator, the 10-K filing dates, and the C05 rev-2 initiation count (10 over 22 prints). The auditor's three independent constructions also reproduce inside the revision-2 models: R06 0.421, R08 0.127, R09 0.246.

Headline numbers, revision 1 → revision 2:

- **R06: 0.55 (0.40–0.68) → 0.46 (0.30–0.60).** What moved it: the size factor is now published as a 0.50 frequency and a 0.75 labelled regime judgement instead of a 0.78 "base rate" shared by all three estimates; the November hazard is a fixed 0.12 judgement instead of a logistic extrapolation into a region the panel never observes; the February rule blends the MLE fit with the hand-set rule because neither is identified on three events. The base-rate estimate, rebuilt without the size judgement, is 0.35; the decomposition 0.47; the anchor is withdrawn (NO_EXTERNAL_ANCHOR). The impact rounds down (EPS 0.00, stock +$1.2, EV +$0.6) and stays immaterial.
- **R08: 0.15 (0.08–0.27) → 0.13 (0.06–0.24).** Convention 2 now converts only booking-generating revenue (the seller-services route is gone), the November conditional falls to 0.035 (no 3Q letter or call has ever previewed the next year numerically), the decomposition is relabelled a judgmental elicitation, and the C05 anchor is withdrawn. The impact rows are corrected: FY27 margin −0.6pp, EPS −$0.06, stock +$3.5 net of a −$1.4 margin debit, EV +$0.5, immaterial.
- **R09: 0.25 (0.14–0.38) → 0.25 (0.13–0.38).** The number does not move; the construction does: the descriptor denominator is 5 not 8, P(figure ≥3%) is 0.55 from the supply-requirement file instead of 0.65 from the wording, the hazard is renamed "descriptor upgraded", the same-day 10-K is a live venue, an aggregation route (two disclosed sub-3% figures summing to ≥3%) is added with the fine print to support it, and the C05 anchor is withdrawn. Impact unchanged (stock +$2, EV +$0.5, immaterial).

All three materiality verdicts survive; none of the three questions is within 10 points of the auditor's number in a way that needs a named asymmetry (R06 +0.04, R08 0.00, R09 0.00).

## Finding-by-finding

### A11-01 (critical, R09) — the model gates on hotels alone, never aggregates: accepted
Reproduced: `r09_model.py:6–10` multiplies a hotel-only hazard by `p_true_ge3` and carries a separate 0.03 "combined sentence" route; convention 2 aggregated in one direction only. With seats at ~2% of the denominator (claim 6, verified at `03_insider_mechanics.md:268`), the true combined share is the hotel share plus about two points, so the question's magnitude test is very likely already met and disclosure is the binding constraint. Fix: convention 2 now says the resolver may add separately disclosed shares of the same denominator from the same window; an aggregation route is added at 0.02 (P(hotel upgraded) 0.30 × P(<3) 0.45 × P(a seats figure also given) ~0.15), below the auditor's 0.025 because the second disclosure is the seats split management refused in 2Q25 ("1% or zero?" — "immaterial"). §4 carries the route; §7 prices it at 0 and 0.05 (0.24 / 0.28).

### A11-02 (critical, R06) — 0.78 is not a base rate and all three estimates share it: accepted
Reproduced: `authorization_history.csv` program sizes 2.0 / 2.5 / 6.0 / 6.0 → 2 of 4 = 0.50, Laplace 0.50; the revision-1 base rate, Monte Carlo and anchor all multiplied by 0.78, and the reported "agree within 5 points" was that shared factor. Fix: the historical frequency 0.50 is published; 0.75 is used in the decomposition as a labelled regime judgement (the two programs since the company reached scale were 1.33–1.58x trailing FCF, which on FY26 FCF $4.4–4.8bn implies $5.9–7.6bn; the first two were 0.59–0.74x, implying $2.6–3.6bn; weight 0.75 / 0.25). The base-rate estimate is rebuilt with no size judgement: three board episodes, Laplace 0.60 for a renewal by the ~1.25-quarter reading, × 0.50 frequency, plus leg B → 0.35. The anchor is withdrawn (below). Revision 2 reports a 12-point disagreement between base rate and decomposition and names its cause instead of averaging it away. 0.78 → 0.75 rather than 0.78 kept: the boilerplate argument for a smaller program is gone (A11-04), which would push the judgement up, but the frequency is 0.50 and the judgement rests on two observations, so it is shaded down one notch and its sensitivity (0.50 → 0.34; 0.90 → 0.55) is shown.

### A11-03 (major, R06) — the trigger rule is hand-set, not fitted: accepted
Reproduced the MLE grid search to the auditor's figures: logit = 1.5308 − 1.4234·r, k 1.423, r50 1.075, nll 4.1107; the hand-set rule scores 4.4924; fitted values 0.527 / 0.456 / 0.438 / 0.322 at r = 1.0 / 1.2 / 1.25 / 1.6 against 0.711 / 0.623 / 0.599 / 0.426. "Fitted to the print-state panel" is withdrawn. Two things the fit itself shows: it has 3 events on 16 rows, and three of the rows (3Q22, 4Q22, 1Q23) are one board episode (A11-16); collapsing that episode to its terminal row leaves all three events at r ≤ 1.6 and every non-event at r ≥ 2.7, i.e. perfect separation and no MLE at all. Neither rule is identified. Revision 2 therefore uses a 50/50 blend of the two evaluated at the simulated reading (0.52 at 1.25 quarters; the three-episode Laplace is 0.60), reports each alone in §7 (MLE only 0.42; hand-set only 0.52), and records the fit in claim 21.

### A11-04 (major, R06) — the "or partnerships" boilerplate: accepted
Reproduced by regex over all 23 letters: "prioritizes investments in organic growth, strategic acquisitions [where relevant | or partnerships], and return of capital to shareholders, in that order" is carried since 2Q22; "or partnerships" first appears in 2Q25 (6 Aug 2025), the letter that announced the additional $6bn. Claim 8 rewritten; the sentence is deleted from the sub-$5bn hypothesis, which now rests on the March 2026 notes' retained ~$500M and RNPL cash timing only.

### A11-05 (major, R06) — the November hazard is an unpriced extrapolation: accepted in part
Reproduced: 3 of 5 at r ≤ 1.6, 0 of 0 in 1.6 < r < 2.7, 0 of 11 at r ≥ 2.7 (Laplace 0.077); 0 of 4 third-quarter prints. Accepted that the logistic's 0.19 at r ≈ 2.2 is an interpolation the log did not price, and the hazard is now a fixed judgement (0.12) with the extrapolation shown. Two parts of the proposed fix are not accepted. (i) The 0-of-4 third-quarter count is not evidence of a November seasonality: 3Q23, 3Q24 and 3Q25 came at r = 3.0 / 4.9 / 7.1, outside any trigger band, and 3Q22 (r 1.0) was the run-to-exhaustion regime — no 3Q print has ever fallen inside the band where the board has renewed (claim 23). (ii) "Unobserved" is a property of the state variable, not of the world: on dollars remaining the November reading (~$2.3bn) sits inside the observed band, between the $1.5bn at which the board renewed (2Q25) and the $2.5bn at which it did not (1Q25). A uniform dollar threshold on that band gives 0.20 × P(recent regime) 2/3 = 0.13; the same construction on quarters of pace (threshold uniform on 1.6–2.7) gives 0.30; the logistic interpolations give 0.17–0.18; the auditor's 0.08 borrows the Laplace rate of the r ≥ 2.7 cell, which is not the cell in question (claim 24). 0.12 is set below the interpolations because the board has never renewed with more than $1.5bn left and the 3Q letter has never carried a program; 0.08 / 0.20 / 0.30 are in §7 (0.46 / 0.50 / 0.53). The choice between 0.08 and 0.12 moves the headline by one point.

### A11-06 (major, R08) — §9 margin and EPS rows contradict their inputs: accepted
Reproduced from the line build (FY27 revenue $15,829M, adj. EBITDA $5,483M, 34.639%): +$158M at the 0.42 flex = +$66M; launch opex $100 / $112 / $125M → 34.086 / 34.011 / 33.930%, i.e. −0.55 / −0.63 / −0.71pp; EPS −$0.047 / −$0.064 / −$0.082. The published −0.3pp corresponded to ~$60M of launch cost and the EPS 0.00 was inconsistent with it. Revision 2 publishes −0.6pp and −$0.06 with the assumption named (half of FY25's $200–250M, midpoint $112M) and the no-launch-cost case (+0.07pp, +$0.09) as the range's top; `r08_v2_impact.csv` carries the table.

### A11-07 (major, R08) — convention 2 converts take-rate revenue that adds no GBV: accepted
Reproduced the contradiction between convention 2 ("any explicit 2027 revenue figure ≥$135M qualifies") and §4 ("sponsored listings would be a take-rate lever whose GBV/nights contribution is nil"). Convention 2 now converts revenue only for products whose bookings pass through GBV and Nights and Seats Booked; pure take-rate and advertising revenue (seller services, sponsored listings, host tooling fees, fee changes) does not convert. The seller-services route is discarded in §4, the February conditional drops 0.12 → 0.10, and the revision-1 convention is priced in §7 (0.14). This is the finding that moved R08.

### A11-08 (major, R08, R09) — C05 as an "anchor": accepted
Reproduced: `bundle-attribution-quantified/forecasts/2026-09-17-forecast.json` is at revision 2 with `p_any_quantification` 0.28 and `anchor: null`; both A11 logs quoted 0.27 from the revision-1 log; R06's JSON carried NOT_INDEPENDENTLY_DERIVED and R08/R09's did not. Both logs now set `anchor: null` (NO_EXTERNAL_ANCHOR), state that the three-estimate requirement is unmet, keep C05 revision 2 (0.28) as a labelled sibling comparison, and no longer report |final − anchor| against it. Applied consistently to R06 as well: its "anchor" was a repo note built as 0.65 × 0.78 (A11-02), so it is withdrawn on the same grounds and kept as a sibling comparison at 0.33–0.49. All three JSONs carry a `sibling_comparisons` block that includes the auditor's independent number.

### A11-09 (major, R09) — descriptor denominator is 5, not 8: accepted
Reproduced: of the 8 rows in `new_business_disclosure_history.csv`, the Goldman row is excluded by convention 1, the 10-K row is a filing not a print, and the 2Q26 letter and call are one print; the seats descriptor was set at 2Q25 (four later prints) and the hotels descriptor at 1Q26 (one later print) → 5. Laplace 1/7 = 0.143 per print, two prints 0.265, × 0.55 = 0.146, plus the other routes → base rate 0.24 (revision 1: 0.21). The base rate and decomposition now agree because they share the corrected inputs, which the log says plainly.

### A11-10 (major, R09) — the 10-K route was discarded on a false premise: accepted in part
Reproduced from the EDGAR submissions JSON: 10-K filing dates 2026-02-12, 2025-02-13, 2024-02-16 against February item-2.02 8-Ks on 2026-02-12, 2025-02-13, 2024-02-13 — two of the last three on the print day; claim 4's "2026-02-13" was wrong and "typically files after the print" was wrong. Corrected; convention 1 now names the 10-K as a live Feb venue. Not accepted as a separate ~0.02 route on the auditor's reasoning: ASC 606 disaggregation in Airbnb's 10-K is by geographic region only (verified, query 17), and a FY26 line-revenue figure would not satisfy any of the question's three tests (a nights/GBV share, or a FY27 revenue figure). The 10-K resolves the question only through a share statement in its KPI discussion, which is the hotel route by another venue; it is carried as +0.02 on the February upgrade hazard (0.18 → 0.20), worth about +0.01 on the headline.

### A11-11 (major, R09) — P(true hotel share ≥3%) had no evidential derivation: accepted in part
Reproduced the supply arithmetic from `hotel_supply_requirements.csv`: 3,914 / 1,957 signed properties per 1m first-year nights at 5% / 10% channel share; 3% of ~575m FY26 nights = 17.2m nights → ~67,500 / ~33,800 / ~16,900 properties at 5 / 10 / 20% share, against "thousands" of hotels in the program; on the NYC anchor (20,000 rooms ≈ 5.8m room-nights a year) scaled to 20 destinations, 3% needs a ~15% channel share; the 11,061 hotel-tagged listings already in the 24-market panel in September 2025 make 2–3% possible. Accepted that the wording inference was not a derivation. Revision 2 puts the unconditional probability at 0.40–0.45 (the file's per-property nights assume boutique-scale properties, ~20 rooms; the NYC supply averages ~200 rooms, so the property counts overstate the requirement) and the conditional at 0.55 via claim 10 (Airbnb volunteers shares that flatter), matching the auditor's number; both are reported, and 0.40 / 0.65 / 0.85 are in §7 (0.22 / 0.29 / 0.34). In part: the auditor's own unconditional 0.40 is at the low end of what the arithmetic supports once property size is accounted for.

### A11-12 (major, R09) — hazard definition double-discounts: accepted
Reproduced the inconsistency between the model comment ("a numeric or mid/high-single-digit hotel share") and the `p_true_ge3` multiplier. The hazard is renamed "descriptor upgraded" (any move from "single-digit" to a number or a finer bucket, including "low-single-digit") and the multiplier is kept as P(the upgraded figure or bucket is ≥3), which under convention 3 equals P(true share ≥3) if management reports truthfully. `r09_model_v2.py` and the JSON `route_split` use the new names.

### A11-13 (major, R06) — two bases for one series: accepted
Reproduced the full letter-vs-cash table (1Q23 500/493, 2Q23 500/507, 3Q23 500/500, 4Q23 750/752, 2Q24 749/749, 3Q24 1,100/1,093, 4Q24 838/838, 1Q25 807/807, 2Q25 1,000/1,010, 3Q25 857/877, 4Q25 1,100/1,095, 1Q26 1,100/1,088, 2Q26 1,100/1,051) and the builder's XBRL tag at `capital_return_panel.py:29`. Convention 3 now states the basis; claim 5 quotes both series; claim 7 reads "$857M as reported in the 3Q25 letter ($877M on the cash-flow line)". The pace distribution is unchanged (last four quarters $0.86–1.10bn on either basis); the letter basis is the one leg B resolves on and the model's threshold is applied to it (next finding).

### A11-14 (major, R06) — letters round $1bn+ quarters to $0.1bn: accepted
Reproduced: sub-$1bn quarters to the nearest $1M (807, 838, 857, 749), $1bn+ quarters to one decimal ("$1.0", "$1.1"; 2Q26 "$1.1 billion" for $1,051M). Convention 3 now says a letter stating "$1.5 billion" resolves Yes, so the effective bar is $1.45bn, and `r06_model_v2.py` tests the simulated quarter at 1.45 (mechanical route 0.0004 → 0.0013; headline unchanged to rounding, as the audit said).

### A11-15 (minor, R06) — readings presented as ranges: accepted
Claim 12 now quotes the three defined readings as points (0.0, 1.2, 1.6; n = 3) with the 2Q22 first program undefined, and says that no print has ever fallen in 1.6 < r < 2.7.

### A11-16 (minor, R06) — five print-states are three episodes: accepted
Claim 22 records the three episodes (2022–23 run-to-exhaustion; Feb 2024 at 1.2; Aug 2025 at 1.6), the base rate is built on episodes (Laplace 0.60), and the interval is widened to 0.30–0.60.

### A11-17 (minor, R06) — impact lines round up: accepted
Reproduced: P(leg B | Yes) 0.0768 / 0.5440 = 0.141; EPS 0.45bn / $165 = 2.727m shares = 0.465% of 586m × $5.73 = $0.0267, weighted $0.004 → 0.00; stock 0.859 × 1.0 + 0.141 × 2.5 = $1.21. Revision 2: P(leg B | Yes) 0.152 from the v2 model, EPS 0.00, stock +$1.2 (weighted $1.23), EV 0.46 × 1.2 = +$0.6. Immaterial verdict unchanged.

### A11-18 (minor, R06) — claim 4 is stronger than its evidence: accepted
The full-text search's 403 is recorded; claim 4 now says "no off-cycle 8-K of a type that has ever carried a repurchase announcement" and points to claim 3 (the note's line 186) as the citation that supports the conclusion. Still non-load-bearing.

### A11-19 (minor, R06) — the buyback event study is not in §6: accepted
Reproduced: `09_event_study_events.csv` rows 775–778 carry Buyback_2.0bn +5.16% (t 1.87), Buyback_2.5bn +2.23% (t 0.87), Buyback_6.0bn +0.22% (t 0.12), Buyback_6.0bn_2 −0.98% (t −0.47) on day 0, each confounded with the print; the prose is at lines 21, 186 and 305 of the note. Claim 3 cites the lines and the rows; §9 now describes the +$1.0 pace-neutral figure as consistent with those four confounded CARs rather than with a section number.

### A11-20 (minor, R08) — "1pt of FY27 growth" convention: accepted
Claim 12 and §9 state the convention: $158M is 1% of FY27 line-build revenue ($15,829M), the brief's own sensitivity; one point of growth on the FY26 base ($14,268M) would be $143M. The row keeps $158M so the memo shows one meaning of "1pt".

### A11-21 (minor, R08) — the stock line ignores the earnings hit: accepted in part
Accepted that the growth credit and the margin debit should be two lines. Not accepted as computed: the auditor capitalised the −0.6pp margin change as if EBITDA fell ~$95M, but the EBITDA dollar change at the $112M launch cost is −$46M (+$66M flex on the new revenue less $112M); the margin-pp change is larger than the dollar change because the denominator grew at a below-average incremental margin. At the market's ~18x FY27 EBITDA ($99bn / $5,483M) over 590m shares the debit is −$1.40/share, not −$2.7. Net stock +$3.5 (growth credit +$4.9, debit −$1.4); EV 0.13 × 3.5 = +$0.46 → +$0.5. Under the fixed-multiple channel the net is +$0.1 and EV ≈ 0. Immaterial either way; the JSON carries both components.

### A11-22 (minor, R08) — the "decomposition" is an elicitation: accepted
Reproduced: with `p_named` at 1.00 the tree gives 0.164 vs 0.151, so the whole answer is the two conditionals. §5 relabels the estimate a judgmental elicitation and writes out the reasoning for each conditional: November 0.035 (a 3Q letter carries no annual guide; a regex over the 3Q22–3Q25 transcripts finds no forward next-year product number, only an analyst asking whether the $200M "proves sticky"); February 0.10 (the Feb letter always previews the year and now carries an FY27 guide; two backward points-figures in 2026; the pricing programme "many multiples bigger than RNPL"; against a 0-of-6 Feb record, Laplace 0.125, and the corrected convention 2). It is about 0.12–0.13, as the auditor said.

### A11-23 (minor, R09) — "of nights booked" vs "of nights and seats booked": accepted
Reproduced: 3.0% of nights = 2.94% of nights and seats at a 2% seats share. Convention 5 added: Airbnb's letters use "nights booked" as shorthand for the reported KPI (the 10-K defines Nights and Seats Booked as nights booked for stays plus seats booked for experiences and services; the 2Q26 sentence "single-digit percentage of nights booked" is about that metric), so a share stated "of nights booked" is accepted without conversion; the strict alternative is priced in §7 (P(≥3) 0.50 → 0.245, i.e. unchanged to rounding).

### A11-24 (minor, all three) — "no news" claims rest on unsaved searches: accepted in part
Accepted the wording: every such claim now reads "no relevant result in the searches recorded". Accepted the snapshot: `curl -sL https://news.airbnb.com/` was saved at 2026-09-17T13:22Z into each question's `sources/` (219 KB; latest items the housing accelerator of 14 Sep, Rijvers CBO of 1 Sep, Q2 results of 6 Aug; no capital-return, product-with-a-number or new-business-metric item). In part: the WebSearch result lists themselves were not re-run to save payloads (the session budget is 5 searches per question and the searches are logged verbatim in `sources/web_search_log.md`); the newsroom snapshot is the primary source for the "nothing new from the company" claims and the search logs remain the record of what was searched.

### A11-25 (minor, R08, R09) — batch coherence unstated: accepted in part
Recorded in both logs (R08 claim 20 and §6; R09 claim 22 and §6) and in both JSONs as a `coherence` block: R09's FY27-revenue route (0.03) ≤ R08 (0.13), and a FY27 revenue figure ≥$500M for a booking-generating line converts to ≥$3.7bn of GBV under R08's corrected convention 2. In part: the inequality holds only because convention 2 now covers booking-generating revenue; under the revision-1 convention any revenue figure converted and the statement was looser. Re-checked after the R08 move: 0.03 ≤ 0.13 holds.

## What the audit missed

1. **The November hazard's "unobserved region" is a property of the state variable (R06).** The auditor's cap rests on the 1.6–2.7 gap in quarters-of-pace. On dollars remaining — the figure the letters actually report and the board actually sees — the November reading (~$2.3bn) sits inside the observed band ($1.5bn renewed, $2.5bn not). The two threshold constructions bracket the hazard at 0.13–0.30, the logistic at 0.17–0.18, the auditor at 0.08; revision 2 takes 0.12 and shows all of them (claim 24, §7).
2. **The 0-of-4 third-quarter count is uninformative (R06).** Three of the four 3Q prints came at r ≥ 3.0 and the fourth in the exhaustion regime; no 3Q print has ever occurred inside the band where the board has renewed, so the count says nothing about a November seasonality (claim 23). The auditor used it as one of three reasons for the 0.08 cap.
3. **The MLE is not identified on episodes (R06).** The auditor raised the three-episode point (A11-16) and the MLE point (A11-03) separately; together they show that collapsing the 2022–23 episode leaves the fit with perfect separation, so "fit the rule and report standard errors" is not an available fix on this panel (claim 21). Revision 2 blends the two rules and says why.
4. **The letter-basis pace (R06).** The last three quarters are all "$1.1 billion" on the letter basis the question resolves on (cash $1,095 / 1,088 / 1,051M), so the letter-basis trailing pace is ~$1.1bn against the panel's cash-basis $1.03bn; a "$1.5 billion" Q4 needs +36% on the letter basis, not +43%. Recorded in claim 6; it does not change leg B's hazard.
5. **The regime-relevant base-rate class (R08).** The 0-of-23 Laplace (0.04 per print) counts sixteen prints in which Airbnb had no new product to quantify. On the seven prints since the new-business strategy was announced (4Q24–2Q26) the record is 0/7 → Laplace 0.11 per print, 0.21 over two prints; on the six Feb letters 0/6 → 0.125. These classes bracket the elicitation from above and are the reason the headline is 0.13 and not the auditor's lower reading of the same tree (claim 18, §5). The auditor's "Laplace on the 0-of-23 record is 0.04 per print" understates the base rate for the prints that matter.
6. **The margin debit capitalises the wrong quantity (R08, A11-21).** See the finding: −$46M of EBITDA, not −$95M; −$1.4/share, not −$2.7.
7. **The 10-K route as described cannot resolve the question (R09, A11-10).** Revenue disaggregation is by geography only, and a FY26 line-revenue figure satisfies none of the three tests; the 10-K counts only via a KPI-discussion share statement. The route is a venue, not a route.
8. **The supply file's property counts assume boutique-scale properties (R09, A11-11).** 511 first-year nights per property at a 10% channel share implies ~20 rooms; the NYC supply averages ~200 rooms per hotel. The requirement in properties is therefore overstated for the kind of supply Airbnb has signed, which is why revision 2's unconditional 0.40–0.45 sits a notch above the auditor's 0.40.
9. **The KPI definition (R09).** The FY2025 10-K defines Nights and Seats Booked as nights booked for stays plus seats booked for experiences and services and excludes HotelTonight from the listing counts; hotel nights booked on Airbnb are stays and are inside the denominator. This is the basis for convention 5 (claim 4).

## Reconciliation with the auditor's numbers

| question | auditor | revision 2 | gap | decision |
|---|---|---|---|---|
| R06 | 0.42 (0.28–0.58) | 0.46 (0.30–0.60) | +0.04 | Inside the noise floor; the gap is the November hazard (0.12 vs 0.08; +0.01) and the blended vs MLE-only February rule (+0.05), less size 0.75 vs 0.78 (−0.02). Held at 0.46: the MLE alone is not identified and over-weights the run-to-exhaustion episode's two non-events at low r (item 3 above). |
| R08 | 0.13 (0.06–0.24) | 0.13 (0.06–0.24) | 0.00 | The auditor's tree (Nov 0.03, Feb 0.10, no naming gate) reproduces at 0.127 inside `r08_model_v2.py`; revision 2's 0.121 with the 0.92 naming gate rounds to 0.13 toward the regime and Feb-class Laplace readings (item 5). |
| R09 | 0.25 (0.13–0.38) | 0.25 (0.13–0.38) | 0.00 | The auditor's construction (0.10 / 0.18, true 0.55, aggregation 0.025) gives 0.246 inside `r09_model_v2.py`; revision 2's 0.12 / 0.20 (the 10-K venue) and aggregation 0.02 give 0.259. Same number, same routes, one venue's difference. |

No question is more than 10 points from the auditor, so no named asymmetry is required; the R06 asymmetry is stated anyway (items 1–3).

## Reproduction output

`py -3.13 -B docs/pitch-forecasts/audits/A11-reproduce.py` from the repo root, 2026-09-17 (script saved verbatim from the audit; no edits; exit 0):

```
========================================================================
R06 / 1. letters vs the capital-return series
quarter | letter $M | XBRL cash $M | diff
  1Q23        500          493      -7
  2Q23        500          507       7
  3Q23        500          500       0
  4Q23        750          752       2
  2Q24        749          749       0
  3Q24       1100         1093      -7
  4Q24        838          838       0
  1Q25        807          807       0
  2Q25       1000         1010      10
  3Q25        857          877      20
  4Q25       1100         1095      -5
  1Q26       1100         1088     -12
  2Q26       1100         1051     -49
letter-stated remaining authorization (USD bn): {'3Q24': 4.2, '4Q24': 3.3, '1Q25': 2.5, '2Q25': 1.5, '3Q25': 6.6, '4Q25': 5.6, '1Q26': 4.5, '2Q26': 3.4}
print  buyback_in_quarter_usd_bn  cash_bn  letter_bn  remaining_after_quarter_usd_bn  remaining_over_pace_q new_authorization_announced
 3Q22                       1.00    1.000        NaN                            1.00                    1.0                          no
 4Q22                       0.50    0.500        NaN                            0.50                    0.7                          no
 1Q23                       0.49    0.493      0.500                            0.00                    0.0                yes ($2.5bn)
 2Q23                       0.51    0.507      0.500                            2.00                    4.0                          no
 3Q23                       0.50    0.500      0.500                            1.50                    3.0                          no
 4Q23                       0.75    0.752      0.750                            0.75                    1.2                  yes ($6bn)
 1Q24                       0.75    0.750        NaN                            6.00                    8.0                          no
 2Q24                       0.75    0.749      0.749                            5.25                    7.0                          no
 3Q24                       1.09    1.093      1.100                            4.20                    4.9                          no
 4Q24                       0.84    0.838      0.838                            3.30                    3.7                          no
 1Q25                       0.81    0.807      0.807                            2.50                    2.7                          no
 2Q25                       1.01    1.010      1.000                            1.50                    1.6       yes ($6bn additional)
 3Q25                       0.86    0.877      0.857                            6.60                    7.1                          no
 4Q25                       1.10    1.095      1.100                            5.60                    6.0                          no
 1Q26                       1.09    1.088      1.100                            4.50                    4.5                          no
 2Q26                       1.05    1.051      1.100                            3.40                    3.3                          no
NOTE 3Q25: panel 0.86 = letter basis; log claim 5 quotes 877 = XBRL cash basis.
capital-allocation boilerplate, every letter that carries it:
    1Q24 -> strategic acquisitions where relevant
    1Q25 -> strategic acquisitions where relevant
    1Q26 -> strategic acquisitions or partnerships
    2Q22 -> strategic acquisitions where relevant
    2Q24 -> strategic acquisitions where relevant
    2Q25 -> strategic acquisitions or partnerships
    2Q26 -> strategic acquisitions or partnerships
    3Q24 -> strategic acquisitions where relevant
    3Q25 -> strategic acquisitions or partnerships
    4Q23 -> strategic acquisitions where relevant
    4Q24 -> strategic acquisitions where relevant
    4Q25 -> strategic acquisitions or partnerships
========================================================================
R06 / 2. trigger rule: author's logistic vs the MLE on the same panel
panel (r, announced): [(1.0, 0), (0.7, 0), (0.0, 1), (4.0, 0), (3.0, 0), (1.2, 1), (8.0, 0), (7.0, 0), (4.9, 0), (3.7, 0), (2.7, 0), (1.6, 1), (7.1, 0), (6.0, 0), (4.5, 0), (3.3, 0)]
r<=1.6: 3/5 | 1.6<r<2.7: 0/0 (UNOBSERVED) | r>=2.7: 0/11, Laplace 0.0769
third-quarter prints: 0/4 announcements
MLE logit = 1.5308 -1.4234*r -> k=1.423, r50=1.075, nll=4.11072
author k=2.0, r50=1.45 -> nll=4.49245 (NOT the MLE)
   r=0.00  MLE=0.8221  author=0.9478
   r=1.00  MLE=0.5268  author=0.7109
   r=1.20  MLE=0.4558  author=0.6225
   r=1.60  MLE=0.3216  author=0.4256
   r=2.20  MLE=0.1679  author=0.1824
   r=2.35  MLE=0.1401  author=0.1419
   r=2.70  MLE=0.0901  author=0.0759
program sizes (USD bn): [2.0, 2.5, 6.0, 6.0] -> P(>=5bn) historical = 0.50 | Laplace = 0.500 | log uses 0.78
========================================================================
R06 / 3. Monte Carlo replay (stdlib random; the saved model uses numpy)
saved r06_summary.csv: {'p_ann_nov': 0.1911, 'p_ann_feb_given_not_nov': 0.5736, 'p_ann_by_feb': 0.6551, 'p_legA': 0.5106, 'p_legB': 0.0768, 'p_yes': 0.544, 'mean_rem_sep': 2.3401, 'mean_rem_dec': 1.2802, 'mean_r_dec': 1.249, 'p_q4_ge_1p5_mechanical': 0.0004}
  author parameters                        {'nov': 0.1917, 'by_feb': 0.6571, 'legA': 0.5123, 'legB': 0.0754, 'yes': 0.545}
  MLE trigger                              {'nov': 0.1702, 'by_feb': 0.5307, 'legA': 0.4145, 'legB': 0.0743, 'yes': 0.4532}
  MLE trigger + size 0.50 (historical)     {'nov': 0.1702, 'by_feb': 0.5307, 'legA': 0.2654, 'legB': 0.0743, 'yes': 0.3168}
  auditor: Nov 0.08, MLE Feb, size 0.78    {'nov': 0.0799, 'by_feb': 0.4884, 'legA': 0.3808, 'legB': 0.0665, 'yes': 0.4198}
  leg B threshold 1.45 (letters round)     {'nov': 0.1917, 'by_feb': 0.6571, 'legA': 0.5123, 'legB': 0.0763, 'yes': 0.5452}
R06 impact arithmetic:
   0.45bn/165 = 2.727m shares; /586 = 0.00465; x FY27 EPS 5.73 = 0.0267
   P(legB|yes) = 0.1412 -> weighted stock = 1.212 (log says 1.3); EV 0.55x1.3 = 0.715
========================================================================
R08 / tree replay and impact arithmetic
saved: [{'metric': 'p_yes_base', 'value': 0.1509}]
replay base = 0.1509 | lenient = 0.2388
base rate 0/23 prints, Laplace 1/25 = 0.0400 -> two prints 0.0784
forward-statement rows: 10 | counting under the R08 convention: 0
auditor tree: Nov 0.03, Feb 0.10 -> 0.1270
   FY27 base margin 34.639%
   launch opex $  0M -> margin 34.712% (delta +0.073pp), EPS delta +0.093
   launch opex $ 60M -> margin 34.336% (delta -0.303pp), EPS delta +0.009
   launch opex $100M -> margin 34.086% (delta -0.553pp), EPS delta -0.047
   launch opex $112M -> margin 34.011% (delta -0.628pp), EPS delta -0.064
   launch opex $125M -> margin 33.930% (delta -0.709pp), EPS delta -0.082
   log states -0.3pp and EPS 0.00; its own stated cost (half of $200-250M) gives -0.63pp and -$0.06
   1pt of FY27 growth on the FY26 base = 142.7M (the brief's $158M is 1% of FY27 revenue)
   EV = 0.15 x 4.90 = 0.735
========================================================================
R09 / route replay, descriptor base rate, disclosure-initiation cross-check
saved: [{'metric': 'p_yes', 'value': 0.2599}, {'metric': 'p_hotel_share_disclosed', 'value': 0.2784}, {'metric': 'p_hotel_route_yes', 'value': 0.181}, {'metric': 'p_other_routes', 'value': 0.0964}]
replay base (p_yes, disc, hotelYes, other) = (0.2599, 0.2784, 0.181, 0.0964)
auditor (Nov 0.10, true 0.55, aggregation 0.025) = (0.2459, 0.262, 0.1441, 0.119)
disclosure-history rows: 8 | conference or 10-K rows: 2
independent upgrade opportunities: seats descriptor set 2Q25 -> 4 later prints; hotels descriptor set 1Q26 -> 1 later print = 5, not 8
   n=5: Laplace/print 0.1429, two prints 0.2653, x0.65 = 0.1724
   n=8: Laplace/print 0.1000, two prints 0.1900, x0.65 = 0.1235
C05 rev-2 matrix: (16, 23) | seed cohort quarter: 1Q21 (6 metrics) | new quantified metrics initiated later: 10 over 22 prints -> 0.4545 per print
                          matrix          window  continued  eligible  continuation  returned  gaps  return_rate
                   rev1_as_coded             All         91       111        0.8198         5    19       0.2632
                   rev1_as_coded W1 target>=1Q23         58        76        0.7632         5    17       0.2941
                   rev1_as_coded W2 target>=1Q24         38        54        0.7037         5    16       0.3125
               v2_partial_recode             All         93       113        0.8230         4    18       0.2222
               v2_partial_recode W1 target>=1Q23         60        78        0.7692         4    16       0.2500
               v2_partial_recode W2 target>=1Q24         40        56        0.7143         4    15       0.2667
v2_excl_GF_cancel_ME_sensitivity             All         81        94        0.8617         3    12       0.2500
v2_excl_GF_cancel_ME_sensitivity W1 target>=1Q23         52        64        0.8125         3    11       0.2727
v2_excl_GF_cancel_ME_sensitivity W2 target>=1Q24         32        43        0.7442         3    11       0.2727
10-K filing dates: ['2026-02-12', '2025-02-13', '2024-02-16'] | February 2.02 8-K dates: ['2026-02-12', '2025-02-13', '2024-02-13']
=> FY2024 and FY2025 10-Ks filed the SAME DAY as the print; R09 claim 4 dates the FY2025 10-K 2026-02-13 and the log discards the 10-K route as 'typically files after the print'
R06 p = 0.55 ci [0.4, 0.68] | stock 1.3 EV 0.7 | EV check 0.715 | material False
R08 p = 0.15 ci [0.08, 0.27] | stock 4.9 EV 0.7 | EV check 0.735 | material False
R09 p = 0.25 ci [0.14, 0.38] | stock 2.0 EV 0.5 | EV check 0.5 | material False
C05 revision 2 p_any_quantification = 0.28 -> R08 and R09 both anchor on the stale 0.27
```

(The last four lines read the revision-1 JSONs as they stood when the script ran; the revision-2 JSONs now carry 0.46 / 0.13 / 0.25 and `anchor: null`.)

Revision-2 model runs (separately, not in the audit script): `r06_model_v2.py` base 0.469 (by Feb 0.576, Nov 0.120, Feb | not Nov 0.518, leg A 0.431, leg B 0.071, P(leg B | Yes) 0.152; auditor's construction 0.421; revision-1 construction 0.554); `r08_model_v2.py` base 0.121, lenient 0.212, auditor's tree 0.127, revision-1 tree 0.151; `r09_model_v2.py` base 0.259 (upgraded 0.296, hotel route 0.163, other 0.114; auditor's construction 0.246; revision-1 construction 0.260).

## Final table

| question | revision-1 | auditor | revision-2 | anchor | \|final − anchor\| | EV $/share | material |
|---|---|---|---|---|---|---|---|
| R06 P(authorization ≥$5bn by the Feb print, or 4Q26 repurchases ≥$1.5bn) | 0.55 (0.40–0.68) | 0.42 (0.28–0.58) | **0.46 (0.30–0.60)** | none (NO_EXTERNAL_ANCHOR; sibling comparisons: audit 0.42, team note 0.33–0.49) | n/a (0.04 vs the audit) | +0.6 (stock +1.2; EPS 0.00) | no |
| R08 P(a letter or call quantifies a ≥1pt / ≥$1bn-GBV 2027 lever for a new or named-2027 booking-generating product) | 0.15 (0.08–0.27) | 0.13 (0.06–0.24) | **0.13 (0.06–0.24)**; lenient 0.21 | none (NO_EXTERNAL_ANCHOR; sibling comparisons: audit 0.13, C05 rev 2 0.28) | n/a (0.00 vs the audit) | +0.5 (stock +3.5 = +4.9 − 1.4; FY27 margin −0.6pp; EPS −0.06) | no |
| R09 P(hotels, Experiences or Services together disclosed at ≥3% of nights and seats or GBV, or a FY27 revenue figure ≥$500M) | 0.25 (0.14–0.38) | 0.25 (0.13–0.38) | **0.25 (0.13–0.38)** | none (NO_EXTERNAL_ANCHOR; sibling comparisons: audit 0.25, C05 rev 2 0.28) | n/a (0.00 vs the audit) | +0.5 (stock +2; no operating delta) | no |
