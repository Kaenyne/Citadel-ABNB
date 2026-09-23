# 43c. The cost leg through the catalysts: does "tails we win" hold, and what does 5 Nov / 11 Feb do to thesis point 3?

Krish with Claude (Fable 5.1), 22 Sep 2026, branch `krish/cost-leg`. Pre-registered in `43c_prereg.md` (written before any 3Q23–2Q24
nights or peer numbers were read for this package). Script `analysis/src/margin_build/43c_catalyst_path/run.py` (`py -3.13 -X utf8`,
exit 0), outputs `data/processed/margin_build/43c_catalyst_path/`. Inputs are all in-repo: `02_panel_quarterly.csv`,
`predictive/02_peer_prints.csv`, the letters and call transcripts (main tree, read-only), `05_statements.csv`, the FY25 10-K and 1Q26/2Q26
10-Q text under `data/raw/regulatory/quantification/`, the C04×C09 joint (`mc_joint_and_conditionals_v2.json`), and the 40/41/42 tables.
No web search was needed; nothing on the kill lists (`AGENT_BRIEF.md` §6, `SYNTHESIS.md` §9) is quoted.

## Bottom line

1. **"Tails we win" does not hold as an evidenced claim.** The one clean episode of a marketing deceleration (S&M cash growth +28.6% in
   2Q23 → +3.8% in 3Q23 → +5.1% in 4Q23) **FAILS** the pre-registered test: Airbnb's nights growth slowed 4.1pts over the next two
   quarters while Booking's room nights slowed 14.5pts and Expedia's 7.5pts over the same quarters; in the cut quarter itself nights
   *re-accelerated* (11.0% → 13.5%). The 2025-26 "paid growth initiatives in emerging markets" step (+24% to +34% S&M y/y for four
   quarters) is **NOT SUPPORTED** as a nights buyer either: Latin America ran 18-21.5% before and during it (1 of 4 quarters ≥ 3pts above
   its 2024 average), Asia Pacific *decelerated* from ~20% to mid/high-teens, and the 2026 acceleration came in North America, a core
   market where management says it does "not add dollar for dollar". Management's own description (performance marketing is "a laser",
   "not a way to buy customers", ROI "in weeks and months"; ~90% of traffic direct or organic; 2020 traffic back to 95% of 2019 with
   marketing switched off) points the same way. A $64M–$177M Q4 trim (13–35% of the $504M Q4 brand-and-performance line in the build)
   is therefore most likely cheap in nights. The honest version for the memo: **if management trims to hold the floor, the cost leg pays
   nothing and the short depends on the revenue leg; "tails" is at best neutral, not a win.**
2. **The 5 Nov cost leg is a 37% tail, not an expected-value engine.** From the audited C04×C09 joint: Q4 sentence "down y/y" (costs
   flagged, the 3Q24 form) 0.22; FY26 floor softened without a Q4 "down" 0.15; floor held with Q4 flat/up (trim-to-hold) 0.25; FY26
   raised to ~36% with Q4 "up y/y" (costs fall on their own; **the cost leg hurts the short**) 0.25; residual 0.13. With the Street's FY27
   response set per branch (−100 / −50 / 0 / +50 / 0bp) and 42's slope, the **probability-weighted cost-leg contribution is −0.4% of NTM
   EBITDA, −0.9% to −1.1% vs QQQ on the slope, −0.4% (≈ −$0.7/share) at a constant multiple.** The tail is real (branch A: −4.9% to
   −6.2% on the cost leg alone; the 8 Nov 2024 precedent was −8.7% on the day), but the cost leg is almost entirely conditional on the
   revenue guide: P(Q4 "down" | guide below Street) 0.30 vs 0.03 otherwise, and P(Q4 "up" | guide not below) 0.78.
3. **February is an estimate event, not a price event, for costs.** A FY27 sentence below the FY26 print is a coin flip (B12 0.49
   literal; 0.36 material), worth −$135M / −$189M of Street FY27 EBITDA (−2.3% / −3.3%) and −$3.9 / −$5.5 a share at a constant
   multiple (EV ≈ −$2/share). But February Q4 prints have been up on the day 6 of 6 times and the one February with a dollar budget
   (2025, floor 190bp below the print) was +14.4%, because November had already paid for it (−8.7%). The tells to score on 5 Nov are
   the ones `42_event_reasons.md` listed: a Q4 sentence that names a cost line, and "2027 investment plans".
4. **The 13 Oct host-only fee migration is a take-rate/GBV object, not a cost object.** No cost effect found beyond a second-order
   reduction in merchant fees through lower GBV (≤ $5M a quarter at half the book).

## 1. Does cutting marketing cost Airbnb nights?

### 1.1 E-2023, the pre-registered test (`43c_e2023_test.csv`, `43c_e2023_summary.csv`)

| quarter | h | ABNB S&M cash y/y | ABNB revenue y/y | ABNB nights y/y | BKNG room nights y/y | EXPE room nights y/y |
|---|---|---|---|---|---|---|
| 1Q23 | −2 | +30.5% | +20.5% | +18.6% | +38% | +22.7% |
| 2Q23 | −1 | +28.6% | +18.1% | +11.0% | +9% | +8.7% |
| **3Q23** | **0** | **+3.8%** | +17.8% | **+13.5%** | +15% | +9.4% |
| 4Q23 | 1 | +5.1% | +16.6% | +12.0% | +9% | +9.3% |
| 1Q24 | 2 | +13.5% | +17.8% | +9.5% | +9% | +7.1% |
| 2Q24 | 3 | +17.1% | +10.6% | +8.7% | +7% | +10.3% |

Registered pass line: PASS iff (i) avg(h=1,2) − avg(h=−2,−1) ≤ −2.0pt for ABNB nights, **and** (ii) that deceleration exceeds the
least-decelerating peer's by ≥ 1.0pt, **and** (iii) the two-year stack also decelerates. Result: (i) met, −4.1pt; (ii) **not met**, BKNG
−14.5pt and EXPE −7.5pt, so Airbnb decelerated *less* than either peer (gap +3.4pt to the nearer peer, against a required −1.0); (iii)
undefined as designed, because the pre-window's two-year base is 2021 (pandemic) — a flaw in the registered design, reported not hidden.
**Verdict: FAIL** (n = 1 episode). Reading: the 1H23-to-2H23 deceleration was industry-wide (the reopening comp), and the quarter in
which Airbnb's marketing growth collapsed was the quarter its nights growth *rose*. Revenue growth stayed at 17-18% through 1Q24.

Caveats registered in advance and confirmed: the 2023 S&M drop was brand-campaign *phasing* ("we pulled forward the timing of marketing
spend to be more heavily weighted in the first half", 2Q23/3Q23/4Q23 letters), not a performance-marketing cut, and 2023 was the
ADR-normalisation year with an easy 1H22 base. The test can say "no evidence that a brand-phasing cut cost nights within three
quarters"; it cannot say a performance cut would be free.

### 1.2 E-2020 (qualitative only, as registered)

2Q20 S&M cash −70% y/y, 3Q20 −74% (panel). Chesky, 4Q20 call (25 Feb 2021): "We pulled back all marketing, including performance
marketing ... Even before we started resuming our marketing spend, our traffic levels came back to 95% of the traffic levels of 2019
without any marketing spend ... In Q4, more than 90% of our traffic was direct or unpaid." 1Q21 letter: the S&M decline was "primarily
due to a decrease in performance marketing expenses. Our strategy is to increase brand marketing and use the strength of our brand to
attract more guests via direct or unpaid channels." Pandemic-confounded; it is management's own claim, consistent with 1.1, not a test.

### 1.3 E-4Q24 (the reverse direction, association only)

The one place the letters tie spend to nights: 4Q24 letter, "During the second half of 2024, we introduced brand campaigns more broadly in
Latin America ... growth in the number of first-time bookers in Latin America accelerate[d] nearly 15 percentage points compared to Q3";
LatAm nights 15% (3Q24) → low-20s (4Q24), with S&M cash +27% / +28% y/y in 3Q24/4Q24 and company nights 8.5% → 12.3%. Confounded by the
Pix local-payment launch named in the same paragraph and by the "acceleration in growth across all regions" that quarter. Brand, not
performance; one region; n = 1.

### 1.4 E-2025/26, the symmetric test (`43c_e2526_regional.csv`)

| quarter | S&M cash y/y | LatAm nights (letter) | vs 2024 avg 18.1 | APAC nights (letter) | vs 2024 avg 20.1 | NA / EMEA |
|---|---|---|---|---|---|---|
| 1Q25 | +8.4% | low-20s | +3.4 | mid-teens | −5.1 | — / high-single |
| 2Q25 | +21.3% | high-teens | −0.1 | mid-teens | −5.1 | softer / — |
| 3Q25 | +24.2% | low-20s | +3.4 | mid-teens | −5.1 | — |
| 4Q25 | +26.3% | high-teens | −0.1 | mid-teens | −5.1 | mid-single / high-single |
| 1Q26 | +34.1% | high-teens | −0.1 | high-teens | −2.1 | high-single / mid-single |
| 2Q26 | +26.4% | ≈20% | +1.9 | high-teens | −2.1 | high-single ("highest in almost three years") / high-single |

10-Q driver for the step: "+$126 million increase in marketing activities driven by paid growth initiatives in emerging markets and
partnerships" (1Q26); "+$132 million ... higher paid growth marketing initiatives in emerging markets and partnerships" (2Q26). Registered
pass line: SUPPORTED iff LatAm and APAC both ≥ +3pts vs their 2024 average in ≥ 3 of the four quarters 3Q25–2Q26 while NA/EMEA did not.
Result: LatAm 1 of 4, APAC 0 of 4; NA accelerated instead. **NOT SUPPORTED.** Word-bucket mapping (low-20s 21.5, high-teens 18,
mid-teens 15, ≈20% 20) is a convention; moving every bucket 1pt does not change the count. Reading: the paid step held Latin America at a
high-teens/20% rate on a larger base and did not lift Asia Pacific; "the average growth rate of nights booked on an origin basis in our
expansion markets was roughly twice that of our core markets" (4Q25/1Q26/2Q26 letters) was already true in 2024 before the step.

### 1.5 Management's own words on what marketing buys (05_statements.csv ids; verbatim)

- Brand vs performance: "the vast majority of our marketing spend ... is not performance marketing. It's brand marketing ... [performance]
  is not necessarily a way to buy customers. It's literally more like a laser" (Chesky, 3Q23 call); "we use our search engine marketing
  as kind of a laser to focus on areas where maybe we have less demand than we have supply" (Stephenson, 3Q23 call); "performance
  marketing as a ... surgical topper to the majority of our spend being in brand" (Mertz, 2Q25, S279).
- Horizon: "From a performance marketing standpoint ... the ROI is very specific and relatively short-term. We think about that in terms of
  weeks and months, not quarters. In terms of brands, we think about that over a longer time horizon" (Mertz, 2Q24, id 211).
- Fixedness: "brand marketing ... is effectively a fixed amount of spend for each market in terms of the minimum amount that you need to
  spend for that market to be efficient"; "in our core markets ... we are not adding dollar for dollar as revenue increases" (Mertz, 4Q24,
  242-243). "It's really actually hard to invest a lot of money in this business" (Chesky, Goldman 8 Sep 2026, V018).
- Traffic: "Nearly 90% of our traffic is direct or organic" (Chesky, Goldman 8 Sep 2026, S371); FY25 10-K: "the strength of Airbnb's
  brand ... has allowed us to maintain lower reliance on paid marketing channels".
- Cuttability: FY25 10-K Note 13 — non-cancelable "other commitments" (which "include ... brand marketing") total $169M, $66M due within
  one year, against $1,595M of FY25 brand-and-performance marketing. Almost all of the line is cancellable inside a quarter.
- The 10-K split (FY25): brand and performance marketing $1,455M → $1,595M (+10%); field operations and policy $693M → $993M (+43%).
  The 10-Q segment table gives the quarterly "Marketing" line: 1Q26 $506M vs $382M (+32%), 2Q26 $600M vs $468M (+28%).

Verdict on "tails we win": **does not hold as evidenced.** Every strand (E-2023 FAIL, E-2025/26 NOT SUPPORTED, 2020 traffic, ~90%
direct/organic, brand-dominant mix, $66M of near-term commitments) says a Q4 trim is feasible and probably cheap in nights inside the
memo's horizon. The repo's own number for the growth cost of a trim, B03 §9's −0.3pt of 4Q26 nights (−$9M revenue), is a judgement with no
elasticity behind it; nothing here justifies a larger one. What the trim *does* do is cap FY26 at 35.5% and leave FY27 estimates
untouched, which is a zero for the cost leg. Counter-evidence to keep in view: M6's asymmetry (S&M k_dn −0.12 vs k_up +1.83, n 16) and
"in the 2025 slowdown management changed nothing" say management has not *chosen* to trim on a deceleration since 2023, so the trim
branch is a decision, not a reflex — which is exactly why C04 (a) is priced with a 0.50 cut probability inside it.

## 2. The 5 Nov and 11 Feb decision tree (`43c_decision_tree_5nov.csv`, `_overlays.csv`, `_11feb.csv`)

Branch probabilities are cells of the audited C04×C09 joint (revision 2, `mc_joint_and_conditionals_v2.json`), which already conditions on
C01 (P(guide below Street) 0.73). I did not re-forecast anything; I partitioned the joint so that each cell maps to one management action.
The Street FY27 margin revision per branch is my assumption, anchored on the precedents in `42_event_reasons.md`; NTM revision =
Δmargin × Street FY27 revenue ($15,819M) / Street FY27 EBITDA ($5,766M) × 0.85 (November NTM weight on FY27, 42); moves use 42's R1
slopes (2.10 W1 / 2.66 W2 per 1% NTM) and a constant-multiple row (1.05× NTM, from `42_scenarios.csv`). Price $166.84 (21 Sep).

| 5 Nov branch (cells) | P | Street FY27 margin | FY27 EBITDA | NTM | vs QQQ, slope W1–W2 | const. multiple | precedent |
|---|---|---|---|---|---|---|---|
| **A. Q4 sentence "down y/y"** (C09 = a; costs flagged, the 3Q24 form) | **0.22** | −100bp | −$158M | −2.3% | **−4.9% to −6.2%** | −2.4% (−$4.0) | 3Q24: Q4 EBITDA cons −9.6%, FY25 margin cons −0.92pt, −8.7% day 1 |
| **B. FY26 floor softened/lowered, Q4 not "down"** (C04 = d, C09 ≠ a) | **0.15** | −50bp | −$79M | −1.2% | −2.4% to −3.1% | −1.2% (−$2.0) | 4Q23: floor 1.6pt below Street, Street cut 0.25pt, −1.7%; 4Q25: "stable", cut 0.27pt |
| **C. Floor held "at least 35.5%", Q4 flat/up** (C04 = a, C09 ∈ {b,c}; trim-to-hold) | **0.25** | 0 | 0 | 0 | 0 (B03 tell inside at ≈0.25: stock ≈ −$3, sign uncertain) | 0 | 1Q23 "marketing costs roughly the same": −10.9% but revenue-driven; no precedent for a cut framed as efficiency |
| **D. FY26 raised to ~36%, Q4 "up y/y"** (C04 ∈ {b,c}, C09 = c; costs fall on their own) | **0.25** | +50bp | +$79M | +1.2% | **+2.4% to +3.1%** | +1.2% (+$2.0) | 2Q26: floor raised, +17.4%; 4Q25 +4.6% |
| E. Residual (raise with Q4 flat/none; held/softened with no Q4 sentence; no FY sentence) | 0.13 | 0 | 0 | 0 | 0 | 0 | — |
| **Probability-weighted cost leg** | 1.00 | **−17bp** | **−$27M** | **−0.40%** | **−0.85% to −1.07%** | **−0.42% (−$0.7)** | |

Overlays that are not joint cells: **R05 sandbag** (3Q26 ≥ 51.5%, 0.22): +$3.5 on the day (R05 §9) and, if the Q3 marketing step slipped
into Q4, a higher chance of a Q4 "down" sentence (B03 sensitivity) — hurts on the day, ambiguous for Q4. **B03 tell** (0.18): lives inside
branch C; if it fires, FY26 +1.2pp / FY27 +1.1pp on the cost side against a growth read. **C01**: the cost leg is a dependent of the
revenue guide — P(A | below) 0.30 vs 0.03 if not below; P(Q4 "up" | not below) 0.78 and P(FY26 raised | not below) 0.49.

**When the cost leg hurts the short.** Branch D (0.25) plus the raise cells in E (bb + bd, 0.07): about a third of the joint has the FY26
sentence raised, and in every such cell the Street's FY27 cost growth (+10.0%, the slowest since the IPO, `41_cost_leg.md`) looks
conservative rather than light. The mechanism is the one management keeps naming: support cost per booking −10% (1Q26) and −16% (2Q26)
y/y "driven in part by ... our AI assistant" (S151, S160), G&A flat on non-income-tax offsets (F2Q26_ga), "we don't need to grow our
head count at levels that we did in the past" (S163). If C01 resolves "not below" (0.27) the tree flips: D-type outcomes dominate and the
cost leg is a +2% to +3% headwind on top of the revenue-leg loss.

**Scale.** The whole cost leg is worth under 1% of expected move against an options-implied event sd of 9.0% (S01). Its value to the
memo is the A tail (22%, −5% to −6% on costs alone, −8.7% precedent) and the February estimate cut, not expected value.

### 11 Feb (`43c_decision_tree_11feb.csv`; B12 rev 2, F03 rev 2)

| February branch | P | FY27 margin vs Street 36.45% | FY27 EBITDA | const. multiple | note |
|---|---|---|---|---|---|
| F1. FY27 floor/point below the FY26 print, or explicit investment year (B12 literal) | 0.49 | −0.85pp | −$135M (−2.3%) | −$3.9 | median gap 0.6pp; 34% of these have a gap under 50bp |
| F1m. Material: gap ≥ 50bp or explicit language (= F03 (d)) | 0.36 | −1.20pp | −$189M (−3.3%) | −$5.5 | the Feb 2024 / Feb 2025 form |
| F2. Qualitative "stable"/"maintain", no number (F03 (e)) | 0.48 | 0 | 0 | 0 | Feb 2026 form; Street cut 0.27pt, stock +4.6% |
| F3. Numeric floor ≥ 35.5% (F03 a+b+c) | 0.16 | 0 | 0 | 0 | never given a floor at/above the prior print |

EV of the February cost leg ≈ −$2/share on estimates (B12 §9), on both readings. **Do not book a February price reaction on top** (B12
rule; S03 owns it): Q4 prints have been up on the day 6 of 6, and Feb 2025 paired a 190bp haircut with +14.4%. The November tells move
this: an explicit "2027 investment plans" sentence on 5 Nov takes B12 literal to 0.60 / material 0.50; a B03 marketing-moderation
sentence takes it down ~0.05.

## 3. What to watch on 5 Nov, and the kill criteria for thesis 3 (`43c_watchlist.csv`; thresholds registered in `43c_prereg.md`)

| disclosure | bar (source) | confirms the cost leg | refutes it |
|---|---|---|---|
| 3Q26 S&M, cash (letter P&L less SBC ≈ $70M) | build $778M (+33% y/y); R05: ≤ $724M means the Q3 step never came | ≥ $800M (spend ahead of budget; Q4 "down" more likely) | ≤ $724M (step did not land; R05 Yes) |
| 10-Q segment table, "Marketing" (brand + performance) | build 3Q26 $541M; 1Q26 +32%, 2Q26 +28% y/y | y/y ≥ +25% (paid step persists into 2H) | y/y ≤ +15% (a trim already under way) |
| 10-Q S&M MD&A driver sentence | 1Q/2Q26: "paid growth initiatives in emerging markets and partnerships" | same driver plus headcount | "optimisation", "efficiency", "lower paid marketing" |
| 3Q26 cost of revenue | build $641M cash; LSEG COGS (41 T3: above in 11 of 14); 4Q26 threshold $575M (DEC-0023) | ≥ $650M and 4Q26 implied ≥ $575M (hosting step real) | ≤ $620M (rebates, no step) |
| Q4 margin sentence | C09 down 0.22 / flat 0.26 / up 0.47 | "decline ... due to higher marketing / product development / AI" (3Q24 form) = A | "up year-over-year" = D |
| FY26 margin sentence | C04 held 0.33 / ~36% 0.30 / softened 0.27 | "approximately 35.5%" or floor removed = B | "approximately 36%" = D |
| 2027 language | 3Q24 form: "share more about our 2025 growth and investment plans" | "2027 investment plans", a named launch programme, "carry into next year" | "maintaining strong margins" only (Nov 2023/2025 form) |
| AI support cost per booking | 1Q26 −10%, 2Q26 −16% y/y; ops cash build $361M | decline stalls (< −5%) or make-good / case-reserve language repeats | ≤ −15% again (support leverage funds the marketing) |

**Kill criteria for thesis point 3 (pre-registered here, scored 5 Nov / 11 Feb):**

- **K1 (5 Nov).** 3Q26 cash S&M ≤ $724M **and** Q4 sentence "up y/y" **and** FY26 raised to "approximately 36%" or higher → the FY26 cost
  leg is dead; retire it from the memo and carry the short on the revenue leg only.
- **K2 (5 Nov).** 10-Q "Marketing" y/y ≤ +15% with an efficiency driver sentence, **and** the Q4 nights descriptor ≥ high-single digits →
  the paid step is being unwound with no visible nights cost; "tails we win" is refuted in real time and must not be printed.
- **K3 (5 Nov).** 3Q26 cost of revenue ≤ $620M **and** support cost per booking ≤ −15% y/y → the hosting/AI-support cost line (DEC-0023)
  is refuted; drop the hosting excess from the FY27 gap.
- **K4 (11 Feb).** FY27 sentence numeric ≥ 35.5% or "stable" **and** Street FY27 margin ≥ 36.3% five sessions later → the cost leg has no
  dated catalyst left; thesis 3 reduces to an undated FY27 estimate risk.
- **Confirmations:** C-A: the Q4 sentence names a cost line → expect Q4 EBITDA consensus −5% to −10% and FY27 EBITDA −2% within five
  sessions (3Q24 form). C-B: "2027 investment plans" → B12 to 0.60. C-C: a fourth cost beat against LSEG COGS in five prints.

## 4. The 13 Oct 2026 host-only fee migration: cost lines or take rate only?

The FY25 10-K describes the mechanics neutrally: "the guest pays the booking amount to the Company, which disburses the booking amount to
the host after check-in, net of the host's service fees. Historically, the Company operated only under a split-fee structure ... In
October 2025, the Company began transitioning to a single-fee structure, charging only the host a service fee" (Note 2, revenue
recognition; `abnb_2025_10k.json`). The payment flow is unchanged — Airbnb still collects the full booking amount from the guest and pays
the host net — so the merchant-fee base (pay-in volume, the 1Q26/2Q26 10-Q's driver for the +$64M / +$68M merchant-fee increases) is
touched only through GBV: the D7 take-rate dossier puts the migrated cohort's GBV 1.6-2.3% lower (the ~14% guest fee leaves the guest
price, the host list price rises by less). At 1.70% of GBV (`40_params.csv`; $459M of 3Q26 cost of revenue in the build) and about half the
book migrated (2Q26 letter), that is a reduction of roughly $2-5M a quarter in merchant fees — second order. Chargebacks are driven "by
growth in GBV and a slight increase in our chargeback rate" (2Q26 10-Q), not by the fee structure; operations and support drivers are
payroll, make-good payouts and case reserves (2Q26 10-Q), with no disclosure tying contacts or refunds to the fee change; the 10-K
carries no cost sentence about the migration at all (A15 audit: "describes the transition neutrally in the revenue-recognition note").
Tranche-2 dates (15 Sep / 13 Oct 2026) come from a host resource page and a PMS notice, not a filing (D7 §8 item 6; `06_fee_timeline.csv`
has the 2Q26 letter's "most remaining hosts ... during 2026"). **No cost effect found**: the migration is a take-rate/GBV object (R04,
D7) with, if anything, a small cost-of-revenue tailwind through lower GBV.

## 5. Catalyst and risk lines for thesis 3, as the memo would print them

**Catalysts**

- **Nov 5 (3Q26 print, after the close).** Three cost disclosures. (1) The Q4 margin sentence: "decline ... due to higher marketing and
  product development expenses" (Nov 2024) cut Q4 EBITDA consensus 9.6% and the stock 8.7% in a day; we put 22% on a Q4 "down y/y"
  sentence and 15% on a softened FY26 floor. (2) The 10-Q "Marketing" line, $506M and $600M in 1Q/2Q26 (+32% / +28% y/y, "paid growth
  initiatives in emerging markets"): ≥ +25% in Q3 means the step persists into a Q4 whose revenue guide we expect below the Street (72%).
  (3) Cost of revenue: above LSEG's COGS estimate in 11 of the last 14 prints; a print ≥ $650M and a 4Q26 run-rate ≥ $575M would put
  the hosting step in the numbers.
- **Feb 11 (4Q26 print).** The FY27 margin sentence. About a coin flip (49%) that it sits below the FY26 print, 36% that it is a visible
  haircut of the Feb 2024 / Feb 2025 kind ("at least 35%", "at least 34.5%" with a $200-250M budget) or an "investment year". Each 100bp
  below the Street's 36.45% is −$158M of FY27 EBITDA (−2.7%) and about −$0.23 of EPS; the Street's FY27 already needs cost growth to slow
  from +15% (FY26E) to +10%, the slowest year since the IPO.

**Risks & mitigants (cost-specific)**

- **Costs fall on their own and the sentence is "up year-over-year."** Support cost per booking is down 16% y/y (2Q26) on the AI assistant,
  G&A is flat on tax offsets, and management raised the FY26 floor twice this year; a raise to "approximately 36%" with Q4 "up" is a 25%
  branch worth +2% to +3% on the cost leg alone (7 Aug 2026 precedent: +17%). *Mitigant:* support is $361M of $2.4bn of quarterly cash
  costs; a 16% per-booking decline is worth about $60M a quarter, less than the $67M Q3 marketing step and the $30M hosting step
  management has already flagged; and this branch is 78% likely only when the Q4 revenue guide is at or above the Street (27%).
- **Management trims Q4 marketing to hold the 35.5% floor and nights do not suffer.** The floor needs a $64M–$177M cut, 13-35% of the
  quarter's brand-and-performance line; only $66M of marketing is committed inside a year; the 2023 phasing cut (S&M growth +28.6% →
  +3.8%) cost no nights relative to Booking or Expedia; ~90% of traffic is direct or organic. *Mitigant:* we do not rely on the trim
  hurting growth. A trim caps FY26 at the floor and leaves FY27 estimates untouched; the short's cost leg is the flagged-cost branch (37%),
  and the revenue leg carries the rest.
- **The Q3 sentence was sandbagged.** A ≥ 51.5% 3Q26 margin (22%) would mean the Q3 marketing step slipped, worth about +$3.5 on the
  day. *Mitigant:* the quarterly sentence has been missed slightly more often than beaten (above it in 4 of 10 quarters), and a slipped
  step lands in Q4 — where it raises the odds of the Q4 "down" sentence the short wants.

## 6. What failed, and honest limits

- E-2023 is one episode, and its third condition (two-year stack) was unmeasurable as registered because the pre-window base is 2021. The
  peer comparison carries the verdict; BKNG's 1Q23 +38% is a China-reopening outlier, so I also checked the nearer peer (EXPE −7.5pt): the
  verdict is the same.
- E-2025/26 uses letter word-buckets mapped to points; the mapping is a convention (stated in the script). It cannot see market-level
  nights, and "paid growth in emerging markets" may be buying share in markets the letters do not name (Mexico, Japan, India get
  first-time-booker and origin-nights mentions, not growth rates).
- The Street FY27 revision per branch (−100 / −50 / 0 / +50 / 0bp) is my assumption from precedents, not a fitted quantity; the slope
  itself is an association (42: analysts revise after seeing the stock). Halving the slope halves every move column.
- The joint is the team's own model (C04 rev 2); its 0.50 cut probability inside the held-floor branch is a judgement the audit
  (A03-09) asked for, not a base rate.
- Parameter count: zero fitted here; five branch revisions and six word-bucket mappings assumed; slopes inherited from 42 (two per
  window).

## RESUME

Done: pre-registration (`43c_prereg.md`), script (exit 0), six CSVs, this note. Not committed. Next agent: (1) on 5 Nov score the watch
list and the four kill criteria in §3 *before* reading the print reaction, and append the 3Q26 10-Q "Marketing" line to
`43c_watchlist.csv`; (2) if the memo prints the "tails we win" sentence anywhere, replace it with the §1 verdict (a trim is cheap in nights
and neutral for the cost leg); (3) if 43a/43b/43d produce a cost-flex elasticity or a hosting schedule, re-run the tree with their branch
revisions in place of the −100/−50/0/+50 assumptions; (4) the 10-K S&M split (brand+performance $1,595M / field $993M, FY25) should
replace the line build's $781M field figure if that was cash ex-SBC — check `40_params.csv` before quoting either.

## Erratum (23 Sep 2026, Codex check `audit/CODEX_THESIS3_TEXT_CHECK.md`)

- The E-2023 code takes `min` over peers while labelling it the least-decelerating peer, and the two-year stacked condition was
  computable (−31pp) though pandemic-confounded. The verdict (FAIL: no evidence the 2023 cut cost nights relative to peers) is unchanged.
- One brand-phasing episode cannot establish that trimming 2026's paid growth spend would be cheap in nights; memo text should make no
  claim either way.
