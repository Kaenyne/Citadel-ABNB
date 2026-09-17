**R06 — submitted probability: 0.55, interval 0.40–0.68.**
Defensible as written: no. The model reproduces exactly, but its two decisive parameters are asserted, not derived.
First fix: stop calling 0.78 a base rate — the historical size frequency is 2 of 4 = 0.50, and all three "independent" estimates multiply by the same 0.78.
Next fix: fit the trigger rule or stop calling it fitted, and cap the November hazard, which sits in a region the panel never observes.
Independent comparison: **0.42** (0.28–0.58); the immaterial verdict survives and should stay.

**R08 — submitted probability: 0.15, interval 0.08–0.27.**
Defensible as written: the headline is close to right; the support underneath it is not.
First fix: repair the §9 margin and EPS rows, which contradict their own stated inputs by about 2x.
Next fix: reconcile convention 2's revenue-to-GBV conversion with §4's correct exclusion of take-rate levers, and drop C05 as an "anchor".
Independent comparison: **0.13** (0.06–0.24); EV is under $1/share on any reading.

**R09 — submitted probability: 0.25, interval 0.14–0.38.**
Defensible as written: the number is close to mine, but it answers a narrower question than the one registered.
First fix: the question asks about the three lines **together**; the model gates on hotels alone and never aggregates two disclosed sub-3% lines.
Next fix: correct the descriptor denominator (5 opportunities, not 8), restore the 10-K route, and derive P(true share ≥3%) from the hotel supply file instead of a linguistic inference.
Independent comparison: **0.25** (0.13–0.38), reached by a different route; the headline survives the repairs, the reasoning does not.

## Scope and verification

Audit date **2026-09-17**, read-only, revision 1 of all three logs. Both interpreters were available; `python` (pandas 3.0.5, numpy 2.4.6) ran the saved models and the reproduction below. No network was used: every market claim was checked against the saved `sources/` snapshots, and no prohibited directory was opened.

All three saved models replay to the published numbers. `r06_model.py` reproduces `p_yes` **0.5440**, `p_ann_by_feb` **0.6551**, `p_legA` **0.5106**, `p_legB` **0.0768** and every row of `r06_sensitivity.csv`; a stdlib rewrite of the same structure gives 0.5450 at N=200,000. `r08_model.py` gives **0.1509** base and **0.2388** lenient. `r09_model.py` gives **0.2599 / 0.2784 / 0.1810 / 0.0964**. None of the three binaries triggers the extreme-probability gate; all three EV lines are arithmetically correct (0.55 × 1.3 = 0.715; 0.15 × 4.9 = 0.735; 0.25 × 2.0 = 0.500) and all three materiality verdicts (immaterial) hold under my own numbers as well as theirs.

The capital-return series was checked against the releases directly. Every remaining-authorization figure in `print_state_panel.csv` is in the letter it cites: 3Q24 $4.2bn, 4Q24 $3.3bn, 1Q25 $2.5bn, 2Q25 $1.5bn plus "an additional $6 billion", 3Q25 $6.6bn, 4Q25 $5.6bn, 1Q26 $4.5bn, 2Q26 $3.4bn, and for the earlier program 4Q23 "$750 million remaining under our prior program", 3Q23 "a total of $1 billion under this authorization", 1Q23 "$0.5 billion" completing the $2bn. All four authorizations and their dates verify. The quarterly repurchase amounts do **not** reconcile to a single basis (finding A11-13).

Disclosure-behaviour base rates were cross-checked against **C05 revision 2**. Its recoded matrix gives continuation 0.823 / 0.769 / 0.714 (All / W1 / W2) and gap-return 4/18, 4/16, 4/15 — a different object from R09's (persistence of an existing metric, not initiation of a new one). The initiation object the matrix *does* support is that Airbnb started **10 new quantified metric disclosures over the 22 prints after the 1Q21 seed cohort**, about 0.45 metric-initiations per print. That brackets R09's 0.12/0.18 per-print hazards for one specific salient metric and is the cross-check the log should have run. C05 rev 2 also now reports `p_any_quantification` **0.28**, not the 0.27 both R08 and R09 quote as their anchor.

Paths below are relative to `docs/pitch-forecasts/questions/`; **R06**, **R08** and **R09** name their folders, and `log`, `model` and `forecast` mean `research-log.md`, `datasets/r0X_model.py` and `forecasts/2026-09-17-forecast.json`.

## Findings

| id | question | severity | file:line or field | what is wrong | how you verified | proposed fix |
|---|---|---|---|---|---|---|
| A11-01 | R09 | critical | `log:39,77,97`; `model:6–10`; `forecast.estimates.route_split` | The registered object is "hotels, Experiences **or Services together** ≥3% of nights and seats booked". The model gates on **hotels alone** reaching 3% and gives a separate 0.03 to a "combined" sentence. The log's own claim 6 puts seats at ~2% of the denominator in FY26 and 2.8% in FY27, so the true combined quantity is the hotel share **plus about two points** and is already very likely ≥3%: the binding constraint is disclosure, not magnitude. Convention 2 applies aggregation in one direction only (a single line ≥3% counts "since the three lines together are then ≥3%") but the model never aggregates two separately disclosed sub-3% lines. | Read `QUESTIONS.md` R09 against conventions 1–4 and `model:6–10`; confirmed the seats path at `docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md:268` ("seats share of denominator 1.3% FY25 → 2.8% FY27 base") and `:284`; `log:39` itself concludes "the ≥3% test is carried by hotels", which is true only for a hotels-alone disclosure. | Add an explicit aggregation route — hotels disclosed below 3% **and** a seats or Experiences figure disclosed, summing ≥3% — and state in the fine print whether the resolver may add two disclosed figures. Adding 0.025 for that route, with P(true hotel ≥3%) at 0.55, gives **0.246**. |
| A11-02 | R06 | critical | `log:86,88,91,93`; `forecast.estimates` | The three estimates are not independent and one is mislabelled. `base_rate_estimate` multiplies the historical 3/5 announcement frequency by "P(size ≥$5bn \| announce) = 0.78 (2 of 4 historically)". **2 of 4 is 0.50** (Laplace also 0.50); 0.78 is a judgement. The same 0.78 then multiplies the Monte Carlo, and the anchor is literally built as 0.65 × 0.78. The reported reconciliation — "the three estimates agree within 5 points" — is an artefact of a shared judgmental factor, so brief rule 7's three-estimate requirement is unmet. | `datasets/authorization_history.csv` `program_usd_bn` = [2.0, 2.5, 6.0, 6.0]; 2/4 = 0.50, Laplace (2+1)/(4+2) = 0.50. Re-ran the saved model with `p_size_ge5=0.50`: P(Yes) **0.436** on the author's trigger, **0.317** on the fitted trigger. | Publish 0.50 as the frequency and 0.78 as a named regime judgement (the last two programs were $6bn at 1.33–1.58x trailing FCF; $5bn is 1.05–1.14x FY26 FCF). Rebuild one estimate that does not use it — e.g. a pure print-state frequency for "any new authorization" — so the three estimates are genuinely three. |
| A11-03 | R06 | major | `log:87`; `forecast.model.structure`; `model:9,20` | The trigger rule is described as "fitted to the print-state panel" / "fitted to the 16-print state panel". It is not fitted: `k=2.0` and `r50=1.45` are hard-coded defaults and `r06_model.py` contains no estimation code. | Maximum-likelihood logistic on the same 16 rows (grid search to 1e-4): logit = 1.5308 − 1.4234·r, i.e. **k = 1.423, r50 = 1.075**, negative log-likelihood **4.1107**; the author's rule scores **4.4924**. The MLE is materially lower through the decisive 1.0–1.6 region (r=1.2: 0.456 vs 0.622; r=1.6: 0.322 vs 0.426). Substituting it moves P(Yes) **0.545 → 0.453**. | Either fit the rule and report the fit (and its standard errors on n=16), or describe it as a hand-set prior and justify k and r50 against the three announcement readings 0.0 / 1.2 / 1.6. |
| A11-04 | R06 | major | `log:80` (hypotheses table); claim 8 | The argument that a sub-$5bn program is plausible rests on "the 2Q26 letter **now** lists 'strategic acquisitions or partnerships' ahead of capital return". There is no change: the sentence "prioritizes investments in organic growth, strategic acquisitions …, and return of capital to shareholders, in that order" is identical boilerplate in every letter that carries it since 2Q22. The only wording change ("where relevant" → "or partnerships") first appears in the **2Q25** letter — the same letter that announced the largest authorization in the company's history. | Regex over all 23 letters: 1Q24, 1Q25, 2Q22, 2Q24, 3Q24, 4Q23, 4Q24 = "where relevant"; 1Q26, 2Q25, 2Q26, 3Q25, 4Q25 = "or partnerships". First "or partnerships" = 2Q25, 6 Aug 2025, alongside the additional $6bn. | Delete this as evidence for a smaller program, or note that its only dated appearance coincides with a $6bn authorization. The March 2026 notes and the cash balance remain legitimate arguments; the boilerplate is not one. |
| A11-05 | R06 | major | `log:77,87`; `model:20`; `forecast.monitoring` 2026-11-05 | P(announce at the 5 Nov print) = 0.19 at a reading of ~2.2 quarters is an extrapolation into a region the panel never observes, and the log says so ("the rule is interpolated") without pricing the extrapolation. | Panel counts: **3 of 5** announcements at r ≤ 1.6; **0 observations at all** in 1.6 < r < 2.7; **0 of 11** at r ≥ 2.7 (Laplace 0.077). Separately, **0 of 4** third-quarter prints (3Q22–3Q25) has ever carried an authorization; all four came at 2Q, 1Q, 4Q and 2Q prints. | Cap the November hazard near 0.08 and say why (unobserved region, no 3Q precedent, 14 months since the last $6bn). With Nov 0.08 and the fitted Feb rule the model gives P(announce by Feb) 0.488, leg A 0.381, **P(Yes) 0.420**. |
| A11-06 | R08 | major | `log:130,131`; `forecast.impact.margin_fy27_pp`, `eps_fy27_usd` | The §9 margin and EPS rows do not follow from the inputs stated in the same rows, by about a factor of two. | Line build FY27: revenue **$15,829M**, adj. EBITDA **$5,483M**, margin **34.639%** (`docs/margin-build/SYNTHESIS.md:299–308`). +$158M at the brief's flex rate (0.42) = +$66M; "half of FY25's $200–250M" = $100–125M of launch opex. Result: margin **34.086–33.930%**, i.e. **−0.55 to −0.71pp**, and FY27 EPS **−$0.047 to −$0.082**. The published −0.3pp corresponds to about **$60M** of launch cost, and the published EPS 0.00 is inconsistent with its own margin row. | Publish −0.6pp and −$0.06 with the launch-cost assumption named, or reduce the assumed launch cost to $60M and say so. The FY25 investment figure is a cost for one launch year, not a run-rate. |
| A11-07 | R08 | major | `log:27` (convention 2) vs `log:78` | Convention 2 converts any explicit 2027 revenue figure to GBV at 13.4% and sets the bar at ≥$135M. §4 then correctly notes that seller services and sponsored listings are take-rate levers "whose GBV/nights contribution is nil". The two cannot both hold: under convention 2 as written, "seller services will deliver $500 million of revenue in 2027" resolves Yes for a lever that adds no GBV and no nights. | Compared `QUESTIONS.md` R08 ("≥1 point to 2027 nights or GBV growth … ≥1pt, or ≥$1bn GBV") with `log:27` and `log:78`; the arithmetic itself checks ($135M / 0.134 = $1.007bn) but applies only to booking-generating revenue. | Restrict the conversion to revenue from bookings that pass through GBV, and add a sentence in the fine print excluding pure take-rate and advertising revenue. This is the convention most likely to decide the question, because seller services is exactly what Chesky sized at Goldman. |
| A11-08 | R08, R09 | major | R08 `log:87–90`; R09 `log:88–91`; both `forecast.estimates.anchor` | The designated anchor for both questions is another forecast produced by this same run (C05), used twice, with no independence flag, and it is stale. R06's JSON does carry NOT_INDEPENDENTLY_DERIVED; R08's and R09's do not. R08 then reports \|final − anchor\| = −0.12 against a number that is not a market and shares the run's own disclosure priors. | `bundle-attribution-quantified/forecasts/2026-09-17-forecast.json` is at **revision 2** with `p_any_quantification` = **0.28** and `anchor: null`, `anchor_source: "… three-estimate requirement unmet"`. Both A11 logs quote 0.27 from §6 of the revision-1 log. | Set `anchor: null` with `NO_EXTERNAL_ANCHOR`, state plainly that the three-estimate requirement is unmet, and keep C05 as a labelled sibling comparison at 0.28. Do not report \|final − anchor\| against it. |
| A11-09 | R09 | major | `log:44,86`; `datasets/new_business_disclosure_history.csv` | "0 upgrades in 8 descriptor-prints" inflates the denominator, which makes the base rate too **low**. Of the 8 rows, one is the Goldman conference (excluded by the log's own convention 1), one is the FY2025 10-K, and the 2Q26 letter and the 2Q26 call are the same print. | Independent upgrade opportunities: the seats descriptor was set at the 2Q25 call, giving 4 later prints (3Q25, 4Q25, 1Q26, 2Q26); the hotels descriptor was set at the 1Q26 call, giving 1 later print (2Q26). Total **5**. Laplace (0+1)/(5+2) = **0.1429**/print → two prints 0.2653 → × 0.65 = **0.172**. | Recount to 5 and rebuild `base_rate_estimate`: 0.172 for the hotel route plus the ~0.10 other routes gives **0.255**, not 0.21. The base rate then agrees with the decomposition for the right reason rather than by offsetting errors. |
| A11-10 | R09 | major | `log:82` (hypotheses table); claim 4; convention 1 | The FY2026 10-K route is discarded on a false premise — "the 10-K typically files after the print" — and claim 4 misdates the FY2025 10-K. | `sources/edgar_submissions_CIK0001559720_20260917T034243Z.json` (in R06's folder, same run): 10-K filing dates **2026-02-12, 2025-02-13, 2024-02-16**; February item-2.02 8-K dates **2026-02-12, 2025-02-13, 2024-02-13**. Two of the last three 10-Ks filed **the same day as the print**; claim 4 says 2026-02-13. | Correct the date and restore the 10-K as a live small route (~0.02): ASC 606 revenue disaggregation is the single most likely place a line-level figure would first appear. Keep the "substantially all … from stays" language as the reason the route stays small, which it genuinely is (verified in `data/raw/filings/abnb_10k_FY2025.htm`). |
| A11-11 | R09 | major | `log:40,77`; claim 5, claim 7 | P(true hotel share ≥3%) = 0.65 has no evidential derivation. Claim 7's arithmetic is s × 30% and identifies nothing about s; the remainder is a linguistic inference ("single-digit for a 1–2% share would more naturally be low-single-digit") plus the team's own 3.5%, which claim 5 states is an **assumption** inside a revenue construction. The repo's hotel supply file, opened in query 6 and then unused, points the other way. | `data/processed/hotel_funnel_audit/hotel_supply_requirements.csv`: **3,914** signed properties per 1m nights at a 5% Airbnb channel share, **1,957** at 10%. Three per cent of ~575m FY26 nights is ~17m nights, i.e. ~**34,000** properties at a 10% channel share, against management's "thousands of boutique and independent hotels across more than 20 top destinations" (2Q26 letter, verified verbatim). Against that, the 24-market panel already carried 11,061 hotel-tagged listings in September 2025, before the May 2026 launch, so a pre-existing hotel/aparthotel base makes 2–3% possible. | Derive the prior from the supply file rather than the wording: unconditional P(≥3%) ≈ 0.40, lifted to ≈ **0.55** conditional on management choosing to volunteer the number (claim 10's own finding is that Airbnb discloses category shares when they flatter). Report both the unconditional and the conditional. |
| A11-12 | R09 | major | `model:7–8` | Definitional inconsistency inside the model. The comment defines `p_hotel_disc` as "a numeric **or mid/high-single-digit** hotel share", which under convention 3 already implies ≥3 on the bucket branch, and the next line multiplies the whole thing by `p_true_ge3`. Either the hazard is "any upgrade from the current bucket" (the multiplier is then right) or it is already conditioned (the multiplier double-discounts). | Read `model:6–10` against convention 3 at `log:28`; `forecast.estimates.route_split` repeats the conditioned wording (`p_hotel_share_disclosed_numeric_or_mid_bucket` 0.28). | Rename the hazard `p_hotel_descriptor_upgraded` (any move from "single-digit" to a number or a finer bucket) and keep the multiplier, or split the branch into "number" and "finer bucket" with the ≥3 test applied only to the first. |
| A11-13 | R06 | major | claim 5, claim 7; `datasets/print_state_panel.csv` vs `data/processed/abnb_capital_return_quarterly.csv` | Two different bases are used for the same series without saying so, and leg B resolves on the basis the model is **not** calibrated to. `abnb_capital_return_quarterly.csv` is XBRL `PaymentsForRepurchaseOfCommonStock` (cash); the letters report a trade-basis figure; convention 3 resolves leg B on the letter. | Letter vs cash, USD m: 1Q23 500/493, 2Q23 500/507, 4Q23 750/752, 3Q24 "$1.1bn"/1,093, 2Q25 "$1.0bn"/1,010, **3Q25 857/877**, 2Q26 "$1.1bn"/1,051. The panel uses **0.86** for 3Q25 (letter basis) while claim 5 and claim 7 quote **877** (cash basis). Builder confirmed at `analysis/src/capital_return_panel.py:29`. | State the basis in the fine print, calibrate the pace distribution on the letter series since that is what resolves leg B, and correct claim 5/claim 7 to "$857M as reported in the 3Q25 letter ($877M on the cash-flow line)". Direction of claim 7 is unaffected. |
| A11-14 | R06 | major | `log:28` (convention 3); `model:32` | The letters round quarterly repurchases to $0.1bn above $1bn — the 2Q26 letter reports "$1.1 billion" for a cash figure of $1,051M. Under the log's own convention 3 ("the dollar figure the 4Q26 letter gives") the leg-B threshold is therefore effectively **$1.45bn**, not $1.50bn, and the model's mechanical test `q4 >= 1.5` is the wrong bar. | Extracted the stated quarterly figure from every letter: sub-$1bn quarters are given to the nearest $1M (807, 838, 857, 749), $1bn+ quarters to one decimal ("$1.0", "$1.1"). Re-running with `legB_thresh=1.45` moves the mechanical route 0.0004 → 0.0013 and P(Yes) 0.5440 → 0.5451. | Write the rounding into convention 3 and use 1.45 in the model. Numerically tiny; the convention matters because it is the resolution rule a judge would apply. |
| A11-15 | R06 | minor | `log:45` (claim 12) | "Historical announcements came at 0, 1.0–1.2 and 1.5–1.6 quarters of pace remaining" presents single observations as ranges. There are three defined readings (0.0, 1.2, 1.6) and one undefined (2Q22, the first program, no prior). | `print_state_panel.csv`: 1Q23 r=0.0, 4Q23 r=1.2, 2Q25 r=1.6; `authorization_history.csv` leaves `remaining_over_pace_quarters` blank for 2022-08-02. | Quote the three readings as points and say n=3. This matters because r50=1.45 was chosen to sit inside a band that does not exist. |
| A11-16 | R06 | minor | `log:86`; claim 12 | The "3 of 5 print-states when ≤1.6 quarters remain" are not five independent board decisions. 3Q22 (r=1.0, no), 4Q22 (r=0.7, no) and 1Q23 (r=0.0, yes) are one episode: the board let the first $2bn run to exhaustion and renewed at the next print. | Read the 3Q22, 4Q22 and 1Q23 letters in sequence; 1Q23 "During Q1 2023, we repurchased $0.5 billion" completes the $2bn and the same letter announces $2.5bn. | Report three independent episodes (2022–23 run-to-exhaustion; Feb 2024 renewal at 1.2; Aug 2025 renewal at 1.6) and widen the interval accordingly. The published 0.40–0.68 is already wide enough to absorb this. |
| A11-17 | R06 | minor | `log:137,138,139`; `forecast.impact` | Both impact lines round up. | P(leg B \| Yes) = 0.0768 / 0.5440 = **0.1412**. EPS: 0.45bn / $165 = 2.727m shares = 0.465% of 586m; × FY27 EPS $5.73 = **$0.0267**; weighted 0.141 × 0.0267 = **$0.004**, which rounds to 0.00, not +0.01. Stock: 0.859 × 1.0 + 0.141 × 2.5 = **$1.21**, so EV = **$0.67**. | Publish EPS 0.00 and stock +$1.2 / EV +$0.67. The immaterial verdict is unchanged and the memo line stands. |
| A11-18 | R06 | minor | claim 4; `sources/edgar_fts_8k_repurchase_20260917T034217Z.json` | "No off-cycle 8-K announces a repurchase program" is stronger than the evidence behind it. EDGAR full-text search returned **HTTP 403**, so only form types and item numbers were read; the three item-8.01 8-Ks of 7 Nov, 14 Nov and 13 Dec 2023 were never opened. | Read the saved 403 response and the submissions index; item lists confirm the form/item pattern but carry no content. | Say "no off-cycle 8-K **of a type that has ever carried one**", and lean on `research/notes/overnight/09_stock-behaviour-and-alpha.md:186`, which states the same conclusion from the letters and is the citation that actually supports it. Claim 4 is already marked non-load-bearing; keep it that way. |
| A11-19 | R06 | minor | claim 3 | The buyback event study is not in §6 of the cited note. §6 is the non-earnings event study and its tables contain peer prints, macro prints, analyst actions and named single events — no buyback row. | The supporting text is at `research/notes/overnight/09_stock-behaviour-and-alpha.md:21`, `:186` and `:305`. The underlying CARs are in `data/processed/overnight/09_event_study_events.csv`: Buyback_2.0bn **+5.16%** (t 1.87), Buyback_2.5bn **+2.23%** (t 0.87), Buyback_6.0bn **+0.22%** (t 0.12), Buyback_6.0bn_2 **−0.98%** (t −0.47) on [0,0], every one confounded with the print. | Cite the line and the CSV rows. The four day-0 CARs, if anything, support the +0.6% "upper plausible bound" the log assumes — quote them rather than a section number. |
| A11-20 | R08 | minor | `log:128`; brief §Sensitivities | "+158 (1pt of FY27 growth)" is 1% of **FY27** revenue ($15,829M), not one point of growth applied to the FY26 base ($14,268M → **$143M**). | `docs/margin-build/SYNTHESIS.md:299` annual table. | Say which convention the row uses. The brief's own wording is loose; R08 inherits it, and nothing downstream changes, but the memo should not show two different meanings of "1pt". |
| A11-21 | R08 | minor | `log:132`; `forecast.impact.stock_usd_per_share` | The stock line takes the full joint-solve $4.90 per point while the same table books FY27 EPS ≈ 0 and FY27 margin −0.3pp, with no offset for the earnings hit the announcement itself implies. | Capitalising 0.3pp of FY27 margin (≈ $47M of EBITDA) at roughly one EV/EBITDA turn per $9–10/share on ~$5.5bn of EBITDA is about **$1.3/share**; at the corrected −0.6pp it is about $2.7. Net stock ≈ **+$3.5** (or +$2.2), EV ≈ **$0.5** (or $0.3). | Show the growth credit and the margin debit as two lines. The immaterial verdict strengthens; the memo clause is unaffected. |
| A11-22 | R08 | minor | `log:86`; `model:6–11` | The "decomposition estimate" contains no data beyond the base rate. `p_named=0.92` barely binds (it scales a small number), so the entire answer is the pair of asserted conditionals 0.05 and 0.12, neither of which is derived from anything in §1. | Replayed the tree: with `p_named` at 1.00 the base is 0.164 versus 0.151 — a 1.3-point swing on the parameter that carries the "decomposition" label. | Relabel it a judgmental elicitation and show the reasoning for 0.05 and 0.12 explicitly (a 3Q letter has never previewed next year numerically; the Feb letter always previews the year and now carries an FY27 guide). Then it is honest, and it is still about 0.13–0.15. |
| A11-23 | R09 | minor | conventions 2–3; claim 1 | The disclosed bucket is "a single-digit percentage of **nights booked**" (2Q26 letter, verified verbatim) while the question's denominator is **nights and seats booked**. The conventions never map one to the other. | With seats at ~2% of the denominator, 3.0% of nights is **2.94%** of nights and seats — a disclosure of "3% of nights booked" would sit on the wrong side of the bar under a strict reading. | Add a sentence: a share stated "of nights booked" is converted to the nights-and-seats denominator at the prevailing seats share before the 3% test, or the resolver accepts either denominator. Say which. |
| A11-24 | R06, R08, R09 | minor | R06 claims 16, 20; R08 claims 14, 17; R09 claims 15, 19; each `sources/` folder | The "no news" claims are stated as facts about the world but rest on one newsroom WebFetch and one shared `Airbnb news this week` search. No saved search response, result timestamp or newsroom snapshot is in any of the three folders. | Inventoried all three `sources/` directories: they hold the Polymarket and Kalshi JSON, the EDGAR 403 and submissions index, and the markdown search logs — no saved result payloads. | Write "no relevant result in the searches recorded" rather than "no capital-return news" / "no product with a number". Save the newsroom HTML and the search result lists. The search logs themselves are unusually good and should be kept. |
| A11-25 | R08, R09 | minor | cross-question | Coherence inside the batch holds but is nowhere stated. R09's FY27-revenue route implies R08 = Yes: a company statement of FY27 revenue ≥$500M for hotels/Experiences/Services converts at convention 2's 13.4% to ≥$3.7bn of GBV, and "hotels at scale" is a named 2027 rollout in R08's own resolution text. | R09 route split `fy27_revenue_ge_500m` = **0.03** ≤ R08 final **0.15**. Satisfied. R06 is independent of both. | Record the inequality in both logs' §6 so the synthesis (X01) can rely on it, and check it again after either number moves. |

## R06 — what the log does well and should keep

The question is answered exactly as written: both legs, the right window, the right resolution source, and conventions 1–4 are written down before the modelling rather than after. The two-leg correlation is handled properly (leg B's hazard rises to 0.14 after a November authorization) rather than being assumed independent.

The capital-return evidence is real and checks out. Every remaining-authorization figure in `print_state_panel.csv` is in the letter it cites, all four authorizations verify with their dates and sizes, and the 3Q26 and Feb readings (mean remaining $2.34bn and $1.28bn, 1.25 quarters of pace) reproduce from the model to four decimals. Claim 7 — no opportunistic step-up after a sell-off — is the sharpest observation in the log and the right one to keep: 3Q25 fell after the −8.0% August print and 1Q26 was flat after the February AI scare.

The impact section is the best in the batch and should be preserved almost verbatim. It correctly identifies that a new authorization changes nothing in the model, because the team's FY27 path already carries $1.05bn a quarter and the reverse DCF already spends $6.3bn — more than the $3.4bn currently authorized. That is exactly the argument a Citadel judge would want: the risk is priced because the base case already assumes it. The distinction between a renewal (no information) and a pace step-change (information) is the right one, and the memo's "a floor on sell-offs, not a catalyst" line survives this audit.

The strongest case against the published 0.55 is already half-present in §4 and should be promoted: the board has renewed exactly twice, from a run of three episodes; the November reading sits in a gap the record never fills; and the size assumption, not the timing, is doing most of the work.

## R08 — what the log does well and should keep

The conventions are the sharpest in the batch. Separating an explicit figure from an order-of-magnitude phrase, excluding conference remarks, requiring a 2027 tie and requiring the statement to be forward-looking are all decisions the question genuinely needs, and each is priced as a sensitivity rather than buried. The lenient-resolver branch (0.24) is the honest way to carry convention risk.

`forward_product_quantification_history.csv` is a genuine contribution: ten dated forward statements, each scored on four independent columns (explicit number / tied to a year / product-specific / counts), and **zero** of the ten pass. The two backward-looking points figures (4Q25 "over 200 basis points … roughly 300 basis points"; 1Q26 "approximately three points … approximately four points") are correctly classified as backward, which is the whole distinction the forecast turns on. Keep that table; it is the evidence.

The forward/backward asymmetry in §5's reconciliation — "management quantifies what a product *did* only when it flatters, and has never quantified what a product *will* do" — is the correct central insight and should go into the memo in that form.

## R09 — what the log does well and should keep

The route decomposition is the right shape: disclosure hazard, magnitude, and several small independent routes, with non-disclosure as the default. Convention 3's bucket mapping ("single-digit" and "low-single-digit" No; "mid-" and "high-single-digit" Yes; "nearly 3%" No) is a genuine resolution rule that a judge could apply, and it is stated before the modelling.

The source work is clean. The 2Q26 letter quotes verify verbatim ("While hotels still represent a single-digit percentage of nights booked … hotel nights booked grew approximately three times as fast as our homes business"; Experiences supply "nearly 80% year-over-year"; seats booked accelerating). The FY2025 10-K language verifies ("For experiences and services, we only earn a host fee. Substantially all of our revenue comes from stays booked on our platform"). All four cited `abnb_declined_to_quantify.csv` rows exist and say what the log says they say, including the 2Q25 Barclays "1% or zero?" exchange and the 2Q26 Mizuho hotels question.

Claim 10 — Airbnb discloses category shares when they flatter and drops series that stop flattering — is the right behavioural model and is independently supported by C05 revision 2's recoded matrix. Keep it, and use it to justify the conditional in A11-11 rather than the linguistic inference the log currently uses.

The impact section's central observation deserves to survive into the memo: a disclosure changes no cash flow, and the same sentence that re-rates the growth story also makes the ADR and take-rate dilution explicit, which supports the short. That two-sided reading is why +$2/share is the right order of magnitude rather than +$5.

## Independent audit numbers

These are audit judgements built from the same repository inputs, not blinded second forecasts or externally anchored probabilities. No tradable market exists for any of the three questions; I confirmed that against the saved Polymarket and Kalshi snapshots rather than refreshing them.

**R06: P(Yes) = 0.42.** Judgmental 80% interval **0.28–0.58**.
Replace the hand-set trigger with the MLE on the same 16-print panel (k = 1.423, r50 = 1.075) and cap the November hazard at 0.08 — 0 of 4 third-quarter prints, 0 of 11 at r ≥ 2.7, nothing observed between 1.6 and 2.7 — keeping pace N(1.06, 0.13), leg B at 0.06/0.14 and P(size ≥$5bn \| announce) at 0.78 as an explicitly labelled judgement.
The model then gives P(any authorization by Feb) **0.488**, leg A **0.381**, leg B **0.067**, **P(Yes) 0.420**; at the historical size frequency of 0.50 it is 0.30, at 0.90 it is 0.47, which is the range the size judgement alone spans.

**R08: P(Yes) = 0.13.** Judgmental 80% interval **0.06–0.24**; under a lenient resolver, 0.22.
Laplace on the 0-of-23 record is 0.04 per print. Cut it to **0.03** at the 5 Nov print (a third-quarter letter has never previewed the following year numerically, and the FY27 guide does not exist yet) and lift it to **0.10** at the Feb print (the FY27 guide, the annual launch preview, a management that gave two backward points-figures in 2026 and a pricing team it calls "many multiples bigger than RNPL").
Union: 1 − 0.97 × 0.90 = **0.127**. The gap to the published 0.15 is the 0.05 November hazard, which I think is too high for a print that carries no annual guide.

**R09: P(Yes) = 0.25.** Judgmental 80% interval **0.13–0.38**.
Upgrade hazard on the corrected five-opportunity denominator: 0.10 at 5 Nov and 0.18 at Feb (the annual review, the new CBO, the promised hotels update, the 31 Dec credit expiry) → P(a hotel-share disclosure) **0.262**. P(the disclosed figure ≥3%) **0.55**: about 0.40 unconditional from the supply-requirement arithmetic, lifted because Airbnb volunteers a category share when it flatters.
Other routes: seats 0.02, GBV 0.02, FY27 revenue 0.03, a combined new-business sentence 0.03, plus the aggregation route A11-01 adds at 0.025 → **0.119**. Union **0.246**. The headline is where the log put it; the construction underneath it is not.

## Reproduction script

Read-only, stdlib plus pandas, no numpy or scipy, no network, no file writes. Run from the repository root with `python -B docs/pitch-forecasts/audits/A11-reproduce.py`. The saved models use numpy; this script re-implements the R06 Monte Carlo with `random` and reproduces the published figures to within Monte Carlo error (0.5450 against 0.5440 at N = 200,000), and reproduces the R08 and R09 trees exactly.

```python
"""A11 read-only reproduction (R06, R08, R09).
Run from the repository root: python -B docs/pitch-forecasts/audits/A11-reproduce.py
Requires stdlib + pandas only (no numpy/scipy). Writes nothing; no network.
"""
from pathlib import Path
import html
import json
import math
import random
import re
import pandas as pd

ROOT = Path.cwd()
Q = ROOT / "docs/pitch-forecasts/questions"
R06 = Q / "risk-buyback-upsize"
R08 = Q / "risk-new-2027-growth-lever"
R09 = Q / "risk-new-businesses-quantified-material"


def plain(path):
    s = path.read_text(encoding="utf-8", errors="replace")
    s = re.sub(r"<(script|style)\b.*?</\1>", " ", s, flags=re.I | re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s)))


# ---------------------------------------------------------------- R06 sources
print("=" * 72)
print("R06 / 1. letters vs the capital-return series")
letters = sorted((ROOT / "data/raw/letters").glob("*.htm"))
stated, remaining = {}, {}
for p in letters:
    t = plain(p)
    q = p.name.split("_")[0]
    m = re.search(r"During Q\d \d{4}, we repurchased \$([\d.]+) (billion|million)", t)
    if m:
        stated[q] = float(m.group(1)) * (1000 if m.group(2) == "billion" else 1)
    m = re.search(
        r"we had (?:the authorization to purchase up to )?\$([\d.]+) billion"
        r"(?: of our Class A common stock| remaining under)", t)
    if m:
        remaining[q] = float(m.group(1))
cap = pd.read_csv(ROOT / "data/processed/abnb_capital_return_quarterly.csv")
cash = dict(zip(cap.quarter, cap.buybacks_musd))
print("quarter | letter $M | XBRL cash $M | diff")
for q in sorted(stated, key=lambda x: (x[1:], x[0])):
    c = cash.get(q)
    if c is not None and c == c:
        print("  %-5s %9.0f %12.0f %7.0f" % (q, stated[q], c, c - stated[q]))
print("letter-stated remaining authorization (USD bn):",
      {k: remaining[k] for k in sorted(remaining, key=lambda x: (x[1:], x[0]))})
panel = pd.read_csv(R06 / "datasets/print_state_panel.csv")
panel["cash_bn"] = panel["print"].map(lambda q: cash.get(q, float("nan")) / 1000)
panel["letter_bn"] = panel["print"].map(lambda q: stated.get(q, float("nan")) / 1000)
print(panel[["print", "buyback_in_quarter_usd_bn", "cash_bn", "letter_bn",
             "remaining_after_quarter_usd_bn", "remaining_over_pace_q",
             "new_authorization_announced"]].to_string(index=False))
print("NOTE 3Q25: panel 0.86 = letter basis; log claim 5 quotes 877 = XBRL cash basis.")

print("capital-allocation boilerplate, every letter that carries it:")
for p in letters:
    t = plain(p)
    m = re.search(r"prioritizes investments in organic growth, (.{0,40}?), and return of capital", t)
    if m:
        print("   ", p.name.split("_")[0], "->", m.group(1))

# ------------------------------------------------------- R06 trigger base rate
print("=" * 72)
print("R06 / 2. trigger rule: author's logistic vs the MLE on the same panel")
rows = [(float(r.remaining_over_pace_q),
         int(str(r.new_authorization_announced).startswith("yes")))
        for r in panel.itertuples()
        if r.remaining_over_pace_q == r.remaining_over_pace_q]
print("panel (r, announced):", rows)
le16 = [y for r, y in rows if r <= 1.6]
mid = [y for r, y in rows if 1.6 < r < 2.7]
hi = [y for r, y in rows if r >= 2.7]
print("r<=1.6: %d/%d | 1.6<r<2.7: %d/%d (UNOBSERVED) | r>=2.7: %d/%d, Laplace %.4f"
      % (sum(le16), len(le16), sum(mid), len(mid), sum(hi), len(hi), 1 / (len(hi) + 2)))
third = [y for (r, y), q in zip(rows, panel["print"]) if q.startswith("3Q")]
print("third-quarter prints: %d/%d announcements" % (sum(third), len(third)))


def nll(a, b):
    s = 0.0
    for r, y in rows:
        z = a + b * r
        s -= y * z - (math.log1p(math.exp(z)) if z < 30 else z)
    return s


lo_a, hi_a, lo_b, hi_b = -5.0, 15.0, -15.0, 0.5
best = (0.0, 0.0, 1e18)
for _ in range(8):
    best = (0.0, 0.0, 1e18)
    ga = [lo_a + (hi_a - lo_a) * i / 200 for i in range(201)]
    gb = [lo_b + (hi_b - lo_b) * i / 200 for i in range(201)]
    for a in ga:
        for b in gb:
            v = nll(a, b)
            if v < best[2]:
                best = (a, b, v)
    a, b = best[0], best[1]
    da, db = (hi_a - lo_a) / 40, (hi_b - lo_b) / 40
    lo_a, hi_a, lo_b, hi_b = a - da, a + da, b - db, b + db
a, b, v = best
print("MLE logit = %.4f %+.4f*r -> k=%.3f, r50=%.3f, nll=%.5f" % (a, b, -b, a / -b, v))
print("author k=2.0, r50=1.45 -> nll=%.5f (NOT the MLE)" % nll(2.9, -2.0))
for x in (0.0, 1.0, 1.2, 1.6, 2.2, 2.35, 2.7):
    print("   r=%4.2f  MLE=%.4f  author=%.4f"
          % (x, 1 / (1 + math.exp(-(a + b * x))), 1 / (1 + math.exp(2.0 * (x - 1.45)))))
hist = pd.read_csv(R06 / "datasets/authorization_history.csv")
k5 = int((hist.program_usd_bn >= 5).sum())
print("program sizes (USD bn):", list(hist.program_usd_bn),
      "-> P(>=5bn) historical = %.2f | Laplace = %.3f | log uses 0.78"
      % (k5 / len(hist), (k5 + 1) / (len(hist) + 2)))

# ------------------------------------------------------------- R06 Monte Carlo
print("=" * 72)
print("R06 / 3. Monte Carlo replay (stdlib random; the saved model uses numpy)")


def r06(pace_mu=1.06, pace_sd=0.13, remaining=3.4, k=2.0, r50=1.45,
        p_size=0.78, legB_base=0.06, legB_auth=0.14, legB_thresh=1.5,
        p_nov_override=None, n=200000, seed=11):
    rng = random.Random(seed)
    nov = feb = yes = a_c = b_c = 0
    for _ in range(n):
        common = rng.gauss(pace_mu, pace_sd * 0.8)
        q3 = max(0.6, common + rng.gauss(0, pace_sd * 0.6))
        q4 = max(0.6, common + rng.gauss(0, pace_sd * 0.6))
        rs = max(0.0, remaining - q3)
        rd = max(0.0, rs - q4)
        pace = (q3 + q4) / 2
        pn = 1 / (1 + math.exp(k * (rs / pace - r50))) if p_nov_override is None else p_nov_override
        an = rng.random() < pn
        af = (not an) and (rng.random() < 1 / (1 + math.exp(k * (rd / pace - r50))))
        ann = an or af
        legA = ann and (rng.random() < p_size)
        legB = (rng.random() < (legB_auth if an else legB_base)) or (q4 >= legB_thresh)
        nov += an
        feb += ann
        a_c += legA
        b_c += legB
        yes += (legA or legB)
    return {"nov": nov / n, "by_feb": feb / n, "legA": a_c / n,
            "legB": b_c / n, "yes": yes / n}


def show(label, d):
    print("  %-40s %s" % (label, {k_: round(v_, 4) for k_, v_ in d.items()}))


saved = pd.read_csv(R06 / "datasets/r06_summary.csv").set_index("metric").value
print("saved r06_summary.csv:", saved.to_dict())
show("author parameters", r06())
show("MLE trigger", r06(k=-b, r50=a / -b))
show("MLE trigger + size 0.50 (historical)", r06(k=-b, r50=a / -b, p_size=0.50))
show("auditor: Nov 0.08, MLE Feb, size 0.78", r06(k=-b, r50=a / -b, p_nov_override=0.08))
show("leg B threshold 1.45 (letters round)", r06(legB_thresh=1.45))
print("R06 impact arithmetic:")
print("   0.45bn/165 = %.3fm shares; /586 = %.5f; x FY27 EPS 5.73 = %.4f"
      % (0.45e3 / 165, 0.45e3 / 165 / 586, 5.73 * (0.45e3 / 165 / 586)))
print("   P(legB|yes) = %.4f -> weighted stock = %.3f (log says 1.3); EV 0.55x1.3 = %.3f"
      % (float(saved["p_legB"]) / float(saved["p_yes"]),
         0.859 * 1.0 + 0.141 * 2.5, 0.55 * 1.3))

# ------------------------------------------------------------------------ R08
print("=" * 72)
print("R08 / tree replay and impact arithmetic")


def r08(p_named=0.92, p_nov=0.05, p_feb=0.12, p_loose=0.25, p_oom=0.45, strict=True):
    p = p_named * (1 - (1 - p_nov) * (1 - p_feb))
    return p + (1 - p) * (0.0 if strict else p_named * p_oom * p_loose)


print("saved:", pd.read_csv(R08 / "datasets/r08_summary.csv").to_dict("records"))
print("replay base = %.4f | lenient = %.4f" % (r08(), r08(strict=False)))
print("base rate 0/23 prints, Laplace 1/25 = %.4f -> two prints %.4f"
      % (1 / 25, 1 - (1 - 1 / 25) ** 2))
h8 = pd.read_csv(R08 / "datasets/forward_product_quantification_history.csv")
print("forward-statement rows:", len(h8), "| counting under the R08 convention:",
      int(h8.counts_under_R08_convention.str.startswith("yes").sum()))
print("auditor tree: Nov 0.03, Feb 0.10 -> %.4f" % (1 - 0.97 * 0.90))
FY26_REV, FY27_REV, FY27_EBITDA = 14268.0, 15829.0, 5483.0
up = 0.42 * 158
base_m = 100 * FY27_EBITDA / FY27_REV
print("   FY27 base margin %.3f%%" % base_m)
for cost in (0, 60, 100, 112, 125):
    m = 100 * (FY27_EBITDA + up - cost) / (FY27_REV + 158)
    print("   launch opex $%3dM -> margin %.3f%% (delta %+.3fpp), EPS delta %+.3f"
          % (cost, m, m - base_m, (up - cost) * 0.0014))
print("   log states -0.3pp and EPS 0.00; its own stated cost"
      " (half of $200-250M) gives -0.63pp and -$0.06")
print("   1pt of FY27 growth on the FY26 base = %.1fM"
      " (the brief's $158M is 1%% of FY27 revenue)" % (0.01 * FY26_REV))
print("   EV = 0.15 x 4.90 = %.3f" % (0.15 * 4.9))

# ------------------------------------------------------------------------ R09
print("=" * 72)
print("R09 / route replay, descriptor base rate, disclosure-initiation cross-check")


def r09(p_nov=0.12, p_feb=0.18, p_true=0.65, p_seats=0.02, p_gbv=0.02,
        p_rev=0.03, p_comb=0.03, p_agg=0.0):
    disc = 1 - (1 - p_nov) * (1 - p_feb)
    hotel = disc * p_true
    other = 1 - (1 - p_seats) * (1 - p_gbv) * (1 - p_rev) * (1 - p_comb) * (1 - p_agg)
    return round(1 - (1 - hotel) * (1 - other), 4), round(disc, 4), round(hotel, 4), round(other, 4)


print("saved:", pd.read_csv(R09 / "datasets/r09_summary.csv").to_dict("records"))
print("replay base (p_yes, disc, hotelYes, other) =", r09())
print("auditor (Nov 0.10, true 0.55, aggregation 0.025) =",
      r09(p_nov=0.10, p_feb=0.18, p_true=0.55, p_agg=0.025))
h9 = pd.read_csv(R09 / "datasets/new_business_disclosure_history.csv")
print("disclosure-history rows:", len(h9), "| conference or 10-K rows:",
      int(h9.event.str.contains("Communacopia|10-K").sum()))
print("independent upgrade opportunities: seats descriptor set 2Q25 -> 4 later"
      " prints; hotels descriptor set 1Q26 -> 1 later print = 5, not 8")
for n_ in (5, 8):
    lap = 1 / (n_ + 2)
    two = 1 - (1 - lap) ** 2
    print("   n=%d: Laplace/print %.4f, two prints %.4f, x0.65 = %.4f"
          % (n_, lap, two, two * 0.65))

matrix = pd.read_csv(
    Q / "bundle-attribution-quantified/datasets/metric_persistence_matrix_v2_4Q20-2Q26.csv"
).set_index("metric")
d = matrix.ne("--")
cols = list(d.columns)
firsts = [cols[list(d.loc[i]).index(True)] for i in d.index if d.loc[i].any()]
seed = sorted(set(firsts))[0]
after = [q for q in firsts if q != seed and q != cols[0]]
n_after = len([c for c in cols if c > seed])
print("C05 rev-2 matrix:", matrix.shape, "| seed cohort quarter:", seed,
      "(%d metrics)" % firsts.count(seed),
      "| new quantified metrics initiated later: %d over %d prints -> %.4f per print"
      % (len(after), n_after, len(after) / n_after))
print(pd.read_csv(Q / "bundle-attribution-quantified/datasets/persistence_rates_v2.csv")
      .to_string(index=False))

sub = json.loads((R06 / "sources/edgar_submissions_CIK0001559720_20260917T034243Z.json")
                 .read_text(encoding="utf-8"))["filings"]["recent"]
tenk = [dt for f, dt in zip(sub["form"], sub["filingDate"]) if f == "10-K"]
feb_prints = [dt for f, dt, it in zip(sub["form"], sub["filingDate"], sub["items"])
              if f == "8-K" and "2.02" in it and dt[5:7] == "02"]
print("10-K filing dates:", tenk, "| February 2.02 8-K dates:", feb_prints)
print("=> FY2024 and FY2025 10-Ks filed the SAME DAY as the print; R09 claim 4"
      " dates the FY2025 10-K 2026-02-13 and the log discards the 10-K route"
      " as 'typically files after the print'")

for slug in ("risk-buyback-upsize", "risk-new-2027-growth-lever",
             "risk-new-businesses-quantified-material"):
    obj = json.loads((Q / slug / "forecasts/2026-09-17-forecast.json").read_text(encoding="utf-8"))
    imp = obj["impact"]
    print(obj["question_id"], "p =", obj["final"]["p"], "ci", obj["final"]["ci"],
          "| stock", imp["stock_usd_per_share"], "EV", imp["ev_stock_usd_per_share"],
          "| EV check", round(obj["final"]["p"] * imp["stock_usd_per_share"], 3),
          "| material", imp["material"])
c05 = json.loads((Q / "bundle-attribution-quantified/forecasts/2026-09-17-forecast.json")
                 .read_text(encoding="utf-8"))
print("C05 revision", c05["revision"], "p_any_quantification =",
      c05["p_any_quantification"], "-> R08 and R09 both anchor on the stale 0.27")
```
