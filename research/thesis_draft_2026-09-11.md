# ABNB Investment Thesis — DRAFT, 11 Sep 2026

_Draft companion to `research/thesis.md`, which is untouched. Written for memo v0
(`deck/drafts/memo_v0_2026-09-11.md`). Every number below is sourced to the post-red-team v2 rebuilds
(B1–B4, A1) or to the 11 Sep synthesis notes; withdrawn claims are excluded by construction._

## One-liner

Airbnb's revenue is converted, not forecast — two-thirds of a quarter comes from the prior quarter's
already-printed GBV — so the 5 Nov 2026 Q4 guide is computable today; reported growth halves into FY27 for
reasons that are a dollar lap, a product lap and a mix identity rather than demand, and the single line that
is genuinely mispriced is the 3Q26 printed take rate. **3–12 month horizon; direction pre-committed to that
one line.**

## Recommendation

- **Rating:** **[LONG / SHORT — pending the 3Q26 printed take rate, 5 Nov 2026].** Pre-registered flip:
  printed take rate **≥ 18.10 %** *together with* a 4Q26 nights guide reiterated at "low double digit"
  ⇒ cover and go long; a reversion to "high single digit" nights with a flat-to-down take rate ⇒ stay short.
  Scored 6 Nov against the frozen card, spec `ABNB-INT-v1`.
- **Current price:** **$181.94** (4 Sep 2026 close — the model's valuation anchor). Spot was **$174.54** on
  9 Sep 2026; refresh both before submission.
- **Price target:** **$179** blended, 12-month (bear $146 × 0.30 + base $177.5 × 0.35 + bull $210 × 0.35).
- **Upside / downside:** **−1.6 % vs the $181.94 anchor; +2.8 % vs the 9 Sep spot** — i.e. near-flat expected
  value with fat two-sided tails (mean absolute earnings move 12.1 %). The trade is the branch, not the mean.
- **Horizon:** 3–12 months (Citadel format). Note the finals (22–24 Oct 2026) **precede** the catalyst
  (5 Nov), so the pitch is pre-positioned and eats the overnight gap.

## Thesis pillars

### 1. A guided quarter is arithmetic, and the guide is a separate object nobody models

`revenue_q = λ_season × [⅔·GBV_{q−1} + ⅓·GBV_{q−2}]`; λ_Q4 = **12.030 %**, within-season range **0.171pp**
over three years (measured, recomputed from the quarterly KPI panel). GBV_2Q26 has printed and GBV_3Q26
prints the same morning management guides Q4, so the Q4 guide carries **no GBV forecast error at the moment
it is set** — hence a small, shrinking cushion: **19 of 19 midpoints beaten, trailing-8 mean +1.86 %, sd
1.006pp** (measured, PIT), against +3.04 % over the first eleven prints. The honest corollary, stated first:
**once guided, guide midpoint × (1 + cushion) IS the forecast and nothing we built beats it** (RMSE ratio to
seasonal naive **0.377 W1 / 0.319 W2**, strict PIT, n = 14 / 10). We claim the guide and the composition, not
a level edge on a guided quarter.

### 2. The FY26→FY27 halving is a dollar lap, a product lap and a mix identity — not demand

Booking-date FX is carried *through* the kernel inside the lagged USD GBV base: **≈ +2.9pp in 3Q26 and
+1.0pp in 4Q26 as an output** (Φ × 0.851, spot held 4 Sep 2026; 95 % lag CS +0.3 to +2.2pp), a −1.9pp step.
The popular **−3.4pp step double counts** (see the four-way reconciliation). The product-bundle lap is RNPL
+ cancellation redesign + total-price display (US lap 3Q26, ex-NA lap 1Q27); the 2Q26 10-Q now confirms in
MD&A that RNPL bookings carry higher cancellation rates. The mix identity: geographic mix is an **output** of
`ADR_blend = Σ_r s_r·ADR_r` — **−1.48pp in 2025, −1.43pp measured on the 3Q26-to-date split** — and bedroom
nights +12 % vs nights +10 % is worth **+0.5 to +0.8pp at a measured elasticity of 0.23**, not ~+2pp; seats
and hotel dilution take −0.5pp off reported ADR and net to zero in revenue. Re-based nights: **3Q26 +9.3 %,
4Q26 +7.6 %.**

### 3. The asymmetry is one line on one date: the 3Q26 printed take rate

Reconciled to one number in a block where GBV ≡ nights × ADR holds exactly: **18.14 %, sd 0.46pp,
P(≥ 18.10 %) = 0.53** at our 3Q26 GBV of $26,550M; at Krish's $25.9bn GBV the same arithmetic gives
**18.60 %, P = 0.85**. **The probability depends on the GBV view, not on the fee**, so we pre-register the
*pair* (take rate and GBV), not the ratio alone. ±45bp on this line is worth ≈ ±$530M of FY27 revenue,
≈ ±3.4pp of growth and ≈ ±1.6 EV/EBITDA turns.

## Variant perception

**We agree with the Street on the FY27 dollar and disagree on its derivative.** Our FY27 is exploratory —
+11.5 % at the published kernel weight with a band of **+9.18 % to +11.52 %** — and the growth edge is
**+0.09pp at w = ⅔ and −2.25pp at w = 0.33** (Zacks, 4 Sep 2026), worth **+0.04 turns** against **±1.12
turns** of kernel-weight indeterminacy. Say it in the first 200 words. The variant view is compositional and
sits in three places: (i) the **guide** is a different object from the print and no sell-side model carries a
cushion parameter; (ii) the growth step is FX + product lap + mix identity, so **both** the bull
"re-acceleration" story and the bear "demand is cracking" story misread the shape — our reviews-index stays
series, the one alternative-data series that beats naive out of sample (RMSE 1.48pp vs 2.16, ratio 0.68),
reads 3Q26 nights **+9.5 to +10.0 %**, i.e. no acceleration; (iii) the three ADR levers the Street reads as
strength are each measured smaller or negative.

## Catalysts

| Catalyst | Expected timing | Impact |
|---|---|---|
| 3Q26 print + 4Q26 guide (the trade) | **Thu 5 Nov 2026**, after close | Resolves the flip pair (take rate vs 18.10 %, GBV vs $26,608M), the Q4 nights bucket, and the stated 3Q26 FX integer. Guide midpoint ours **$3,161M** no fee step / **$3,179M** with the θ = 0.83 step; 80 % band $3,012–3,312M |
| 4Q26 print + FY27 / 1Q27 guide | **Feb 2027** | FY27 guide wording crystallises forward growth; on our build the Street marks FY28 forward growth down ~1.5pp ⇒ ≈ −0.72 turns |
| 1Q27 print — the ex-NA bundle lap | **May 2027** | The ex-NA RNPL / cancellation-redesign lap lands (5–6 of 13 weeks); first clean read on whether the nights step is lap or demand |
| Fee-migration deadlines (15 Sep / 13 Oct 2026) | Sep–Oct 2026 | **Dated assumption, not disclosure.** Listed prices rise at payout-neutral pricing with ~no effect on all-in price, GBV or ADR — listed-price readers will print a spurious 4Q26 ADR acceleration |
| Consensus re-pull for nights / ADR / GBV | **2–3 Nov 2026** | Zacks posts operating-KPI consensus 2–3 days ahead; the gap test is defined against a vendor-stamped vintage or not at all |

## Key risks & mitigants

| Risk | Probability | Mitigant / how the thesis survives |
|---|---|---|
| The take rate clears 18.10 % and we are short the flip | 0.53 (our own P) | The flip is pre-registered and sized to be reversible: ≥ 18.10 % **with** a reiterated "low double digit" nights guide ⇒ cover and go long, target $205–215 |
| 3Q26 GBV prints high and the guide clears the panels | material | The test resolves on a **0.22 % move in GBV**; clearing 18.10 % needs revenue ≥ $4,805M, above the top of the $4,690–4,770M guide range. Tell: **GBV > $26,608M** |
| The dollar | largest unmodelled term | ±1sd parallel paths move FY27 FX +2.8 / −1.8pp = **$657M**, more than the whole four-way method spread. Tell: the revenue-weighted basket on FRED H.10, weekly, plus the 5 Nov FX integer (+3 backs the kernel; 0/+1 backs the short-lag fit; +2 ambiguous) |
| Kernel weight is not identified (w ∈ [0.33, ⅔]) | certain | Disclosed, not hidden: it is worth 2.34pp of FY27 growth and ±1.12 turns — ~25× our level edge. It is the reason the pitch is composition, not level |
| RNPL cancellation drag is larger than modelled | 0.30 (bear branch) | Score **funds payable y/y** (+5–11 % = on schedule; < +3 % = larger unpaid book), **not** unearned fees — the single-fee migration confounds that line from 4Q25 |
| The like-for-like pricing residual mean-reverts (4.6 → 2.4pp) | carried as the ADR downside, not a tail | Reported ADR would be ≈ +0.8 % rather than +3.0 %, ≈ $2.2bn of annualised GBV. Hotel ADR +0.6 % by mid-Aug and lodging CPI 4.9 → 3.1 % both point that way; nothing measured points the other way |
| Pre-positioning risk: finals 22–24 Oct precede the 5 Nov catalyst | certain | Stated up front. No drift rule is used anywhere in this pitch, and no event-implied move is quoted: there is no quotable ABNB implied move (the 6 Nov weekly is not listed) |

## Valuation summary

Conventions (`model/assumptions.md`, WS25): every price is a **12-month target** to a ~30 Sep 2027 date on
FY2027E exit metrics, **+0.48 EV/EBITDA turns per point of forward revenue growth, applied once**. At
$174.54 the stock is **16.1× FY27E adj. EBITDA** against an independently derived fair band of **13.5–18.5×,
base 16.5×** — roughly fair, not stretched. The 30.9× a bear quotes is a different EBITDA definition and is
not used. Stated tension: the six-lens football field, discounted to the same date, means **$154–157**,
below the base branch below.

| Case | Price target | Probability | Key assumption |
|---|---|---|---|
| Bull | **$205–215** | **0.35** | 3Q26 printed take rate **≥ 18.10 %** *and* Q4 nights reiterated "low double digit" ⇒ FY27 marked to $16.1–16.3bn, ≈ +2pp of forward growth, ≈ +1 turn. This is the flip: we cover and go long |
| Base | **$170–185** | **0.35** | In line; FY26 guide raised a notch; Q4 guide midpoint $3,145–3,215M, i.e. our $3,161–3,179M inside the range and inside every vendor anchor's error bar |
| Bear | **$140–152** | **0.30** | Q4 nights guided "high single digit" (the RNPL/bundle lap) with a flat-or-down printed take rate and FY26 merely reiterated. Historical analogues on a nights-bucket reversion: −13.4 % (2 Nov 2022), −10.9 % (10 May 2023), −8.0 % (7 Aug 2025) |

**Blended 12-month target $179** (−1.6 % vs the $181.94 anchor, +2.8 % vs the 9 Sep spot). If the team is
not comfortable with a near-flat expected value on the single name, the risk-managed expression is
**short ABNB / long BKNG**, which isolates the take-rate, geo-mix and bedroom-nights calls from travel beta.

---

### Stamps

Backtests are **strict point-in-time** unless marked full-sample (W1 = 14 guide dates from 1Q23, W2 = 10 from
1Q24). Consensus carries vendor and the vendor's own date; **LSEG-family and Yahoo are one panel**, counted
once. **Measured:** the kernel, λ, the cushion, geographic mix, party size (+0.8pp), the bedroom elasticity
0.23, the reviews-index slope. **Assumed:** the fee step (θ = 0.83 is a histogram bin midpoint from a
*voluntary* sub-sample), seats ticket prices, the regulatory drag, FY27 flat-spot FX, the 15 Sep / 13 Oct
deadlines. **Unidentified:** **+2.8pp of like-for-like price and sub-regional mix — a 2-d ridge we refuse to
split**, the RNPL cohort cancellation curve, hotel commission, seats volume. FY27 objects are **EXPLORATORY**
— no annual slot exists in the harness and LIVE rows are scored in nothing; `survives_both_windows = False`
on take rate, guide_mid and FX means **no baseline exists**, not tested-and-failed. `harness/score.py` was
not run for this draft. *Research, not investment advice.*
