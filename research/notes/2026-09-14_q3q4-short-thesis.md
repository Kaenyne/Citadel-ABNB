# ABNB short, 3Q26 / 4Q26 — thesis construction

14 Sep 2026 · jessie/nights-driver-v7 · supersedes `nights_simple.py` (deleted)

Scope is deliberately two quarters. Everything below is either measured from a filing/call, derived
from the team's models, or flagged ASSUMED in-line. Where a leg cuts against the short it is kept
on the record and labelled.

---

## 0. What Krish's RNPL share actually is — the number that broke my old model

From `data/processed/rnpl_short_audit/rnpl_nights_module_params.csv`:

| period | RNPL share of **GBV** | status |
|---|---|---|
| 3Q25 / 4Q25 | 2.5–6% / 7–12% | **assumed** — no 2025 quarterly share has ever been disclosed |
| 1Q26 | ~20% | **measured** — 1Q26 shareholder letter, ledger D031 |
| 2Q26 | "over 20%", used at 21% | **measured lower bound** — 2Q26 call, D043 |
| 3Q26 onward | 21–27% | **assumed** — direction supported by the July 2026 eligibility expansion (D044) |

The share is of **GBV, not nights**, and RNPL bookings carry **1.33× the ADR** of non-RNPL ones
(derived: 1Q26's ~4pts of GBV on ~3pts of nights). So

```
p = s / (r(1-s) + s),   r = 1.33
s = 21% of GBV  ->  p = 16.7% of nights
```

My `nights_simple.py` put RNPL at **50% of bookings in 2026**. That was roughly 3× too high, and
because the cancellation drag scales with the share it made my cancellation leg about twice the
size it should be. The audit (`docs/rnpl-short-audit/01_*.md`, point 8) also found my `C(t)` and
Krish's propensity tail are the same object, and my `L(t)` and PR #32's fitted +2.40 / +2.29 are
the same object. Carrying both double counts. `nights_simple.py` is deleted; the replacement
(`analysis/src/nights_short_q3q4.py`) is an **overlay** on the team's module and adds no mechanism
the team already carries.

## 1. The nights call

Team unified module, base case: **3Q26 +9.49%** (146.3mm), **4Q26 +7.61%** (131.2mm).
Overlay adds two variant views and nothing else:

| | 3Q26 | 4Q26 |
|---|---|---|
| team module base | 9.49% | 7.61% |
| V1 RNPL share above consensus (30/38% GBV vs Krish 24/27%) | −0.15 | −0.20 |
| V2 World Cup cancellation-mix washout | −0.48 | −0.18 |
| **short case** | **8.86%** | **7.23%** |

Against a 3Q26 guide of **10–12%** that is 2.1 points below the midpoint.

**Three independent nowcasts sit below the guide — but they are weak evidence, and I over-sold
them in the first draft of this note.**

| method | 3Q26 nights YoY | file |
|---|---|---|
| NTTO overseas inbound QTD | +9.17% | `q3nowcast/G/G_nowcast_3q26_observable.csv` |
| NTTO Western Europe QTD | +9.40% | same |
| TSA QTD-72 | +7.45% | same |
| Inside Airbnb review index, equal / median weighted | +9.20 / +9.23% | `q3nowcast/E_aug/q3_2026_nowcast.csv` |
| this overlay | +8.86% | `nights_short_q3q4.csv` |
| naive carry-forward | 10.34% | — |
| **guide midpoint** | **11%** | — |

**The walk-forward scoreboards say do not lean on these.** From `q3nowcast/G/G_backtest_scoreboard.csv`,
share of specifications that beat a naive carry-forward out of sample:

| feature family | W1 (2022Q1+) | W2 (2023Q1+) | best ratio |
|---|---|---|---|
| NTTO US inbound | 7 / 24 | 9 / 24 | 0.72 |
| TSA air throughput | 2 / 12 | 3 / 12 | 0.92 |
| Hotel RevPAR | 2 / 16 | 6 / 16 | 0.67 |
| Spain INE | **0 / 40** | 14 / 40 | 1.00 |
| Eurostat platform | **0 / 12** | 1 / 12 | 1.03 |
| BLS CPI price | **0 / 24** | 8 / 24 | 1.32 |

Only a minority of specs beat naive in *either* window, and Spain INE / Eurostat / CPI fail W1
outright — so under this repo's own two-window rule (CLAUDE.md §2) they are not quotable. The
0.74 walk-forward ratio I quoted for NTTO is the **best of 24 specs**, i.e. selection. The Inside
Airbnb review-index nowcast is worse on this test than it looks: `q3nowcast/E_aug/backtest_scoreboard.csv`
shows **465 of 2,560 specs (18%) beat naive**, and only 70 (2.7%) beat it by 20%. A 2,560-spec search
with an 18% hit rate is an overfitting machine.

**Honest status: the nowcasts are directionally consistent with a sub-guide print and that is all
they are.** They are a reason to hold the view, not evidence to pitch. The quotable part of the
nights call is the *lap arithmetic*, which is disclosure-dated and does not depend on any of this.

**Counterweight, and it decides the trade structure:** Airbnb has **beaten the top of its own
nights range both times it gave one** — 4Q25 guided 4–6%, printed 9.82%; 1Q26 guided 7–9%, printed
9.15%. A short that needs them to miss a guide they habitually beat is the wrong trade. The
February 1Q27 guide against a +17.9% comp is the better expression; these two quarters are the
setup.

## 2. Thesis legs — scorecard

| leg | verdict |
|---|---|
| 1. The lap, not the cancellations | **KEEP — lead with it.** Disclosure-dated, team-modelled |
| 2. RNPL share above consensus | KEEP — supporting |
| 3. World Cup cancellation-mix washout | KEEP — new, but parameters are judgment |
| 4. RNPL destroys the float | **KEEP — strongest measured leg** |
| 5. Vacation destinations rolling over | ❌ **DROPPED** — fails four tests, see below |
| 6. Hotel share ceiling | ⚠️ **CUT — this is a long argument** |
| 7. Macro: front end down, long end up | **KEEP — the transmission channel for leg 4** |



### Leg 1 — the lap, not the cancellations (the audit's own conclusion)

"The short is a lap thesis, not a cancellation thesis. Anyone pitching RNPL cancellations as the
driver is pitching the small term." The cancellation drag is **−0.3 to −0.9 points of 3Q26**; the
level lap plus the ex-NA correction is **1.4 to 2.6 points by 4Q26**. Management sized the
2025–26 product bundle (RNPL + cancellation-policy redesign + single-fee migration) at ~2pts of
nights on the 4Q25 call and ~3pts on 1Q26. It is a **level** effect: it lifts the growth *rate*
only while it is still rising, and contributes exactly zero once lapped. The lap dates are
disclosed — **US 3Q26, up-funnel merchandising 4Q26, global 1Q27** — so 4Q26 is the first quarter
where m1 turns negative in the team's own base case (−0.59pts) and 1Q27 is where it bites.

### Leg 2 — RNPL share runs above what's in the numbers

Krish assumes 21–27% of GBV from 3Q26. It went ~0 → 20% of GBV in four quarters and the July 2026
eligibility expansion is disclosed but unquantified. A 30–38% path is not aggressive. Because the
propensity drag scales with the nights share, a higher share mechanically deepens the tail. And the
10-Q says it plainly: *"RNPL bookings have experienced higher cancellation rates."*

### Leg 3 — the World Cup suppressed the observed cancellation rate, and that reverses  [NEW]

FIFA 2026 ran **11 Jun – 19 Jul** across 16 US/Canada/Mexico host cities — "millions of guests",
150k+ new listings, ~14% first-time users; management called it "one obvious contributor" to NA's
best quarter in ~3 years. Event travel is **date-locked against tickets and flights**, so it
cancels far less than the platform average. Those stays were **booked in 4Q25–2Q26** — which is
exactly the window the Street is extrapolating the cancellation rate from. As the cohort washes
out, the aggregate cancellation rate reverts **up on mix alone**, before any RNPL effect. Two
counts, same direction. No team model carries this.

*Honesty flag:* the two parameters (WC share of the comp, event-vs-normal cancellation gap) are
**unsourced judgment** — Airbnb has never disclosed cancellation by trip type. The mechanism is
solid; the magnitude is a guess, sized deliberately small. Pitch the mechanism, not the number.

Note the Street already has "World Cup comp in 2027" on its bear list. The variant here is not the
*revenue* comp — it's the *cancellation-mix* comp, which nobody is modelling.

### Leg 4 — RNPL is a float-destruction story, and it is already visible in the P&L  [STRONGEST]

This is where "RNPL lowers margins" actually has measured evidence. Airbnb's cash model has always
been: collect from the guest **at booking**, pay the host **at check-in**, earn interest on the
float in between. The 2Q26 10-Q describes what RNPL does to that in its own words:

> **"no unearned fees, no operating cash flow until payment"**

Quantified in `rnpl_short_audit/qog_cash_reality_transition.csv`:

- unearned-fee shortfall vs. the seasonally-normalised level: **1Q26 −$442mm (−13.9%)**, **2Q26 −$466mm (−14.1%)**. Before 1Q26 the same series ran within ±5%.
- in-quarter FCF drag: **1Q26 −$340mm**, 2Q26 −$24mm. Forward (`qog_cash_reality_forward_drag.csv`): 4Q26 −$11mm, **1Q27 −$276mm central / −$339mm bear.**

And it has already reached the income statement, where it is **~100% margin**:

- **interest income 2Q26 $183mm vs 2Q25 $190mm; 1H26 $338mm vs 1H25 $363mm — down, while GBV grew 16–19%.**
- FY2023 $721mm → FY2024 $818mm → FY2025 $705mm.

Airbnb is valued on free cash flow. This leg says the FCF line is structurally impaired by the same
feature that is flattering the nights line, and the impairment grows with adoption — i.e. Leg 2 and
Leg 4 are the *same* variable pushing both directions at once. That is the cleanest short
construction available: the bull case for nights **is** the bear case for cash.

Sizing caveat: merchant fees are a real and growing cost line (FY2025 cost of revenue +$208mm, of
which **+$188mm merchant fees**) but Airbnb has never split them by payment timing, so no RNPL
attribution is possible. Refunds are stated as immaterial. Do not claim a P&L cost leg beyond
interest income.

### Leg 5 — vacation destinations  ❌ **TESTED AND DROPPED**

The first draft of this note pitched falling air traffic into leisure destinations (Cancun −11.5%,
Las Vegas −9.3%, Japan −6.8%, Orlando −4.8%) as a short leg. It fails four separate tests. Recording
the failure rather than deleting it, per CLAUDE.md §3.

**1. Airbnb is barely in those places.** Ranking Inside Airbnb's 120 covered markets by trailing-12m
reviews (the demand proxy), the destinations in that table are small or absent:

- **Orlando and Cancun are not covered at all.**
- Las Vegas (clark-county-nv) = **1.08%** of covered-market demand. Fort Lauderdale 1.20%. Hawaii 1.93%. Tokyo 2.94%.
- The actual top markets are **São Paulo 3.77%, London 3.59%, Rome 3.57%, Paris 3.52%, Mexico City 3.09%**.
  `top_airbnb_cities_listings_airports.csv` says the same thing by listings: Paris 40,362 vs **NYC 10,069 and LA 9,919**.

Airbnb's demand base is European capitals and LatAm metros — not US/Caribbean sun-and-sand resorts,
which is where the air data was weak. The leg was measuring the wrong markets.

**2. There is no city-level revenue disclosure, so the "% of revenue" question cannot be answered.**
Airbnb reports four regions and nothing below that. Any city-share number would be my construction
off Inside Airbnb's coverage, which is a regulatory-interest sample, not a representative one. I can
bound it — no single city looks like more than ~4% of demand — but I cannot source a revenue share.

**3. Airbnb's own forward booking pace does not corroborate it.** `q3nowcast/F/F2_q3_in_progress.csv`
measures lead-time-adjusted booked listing-nights for Sep 2026 vs 2025 across 30 markets. Weighting
by market demand:

| region | n | weighted YoY |
|---|---|---|
| LatAm | 5 | **+2.99pp** |
| NA | 6 | +0.15pp |
| APAC | 15 | −0.75pp |
| EMEA | 4 | −1.73pp |
| **ALL** | **30** | **+0.03pp** |

Dead flat. And the EMEA figure is carried entirely by **London −7.20pp**, which is the least reliable
row in the file: a 14-day window with a **+26.9-day horizon offset** between the 2026 and 2025
snapshots, against a maximum of 12.8 days everywhere else. **Excluding London: EMEA +0.61pp, global
+0.72pp — positive.** Booked pace is flat-to-up, not rolling over.

**4. Destination travel data has never moved this stock.** `abnb_big_moves_7pct.csv` — all 41 daily
moves ≥7% since the IPO: **20 macro/market, 11 earnings, 9 company/other, 1 competitor. Zero** driven
by destination or travel-volume data. Earnings moves average **12.1% absolute, 11.3% excess vs QQQ**.
The stock trades on the print and on rates. A soft airport series is not a catalyst and has never been
one.

**What survives:** nothing pitchable. If a version of this leg is ever revived it has to be built on
the markets that actually matter (São Paulo, London, Rome, Paris, Mexico City) and on Airbnb booking
data, not airport throughput — and right now that data is flat to positive.

### Leg 6 — hotel share  ⚠️ **THIS IS A LONG ARGUMENT, NOT A SHORT ONE**

Stating this plainly because the first draft tried to have it both ways. Platform STR share of EU
commercial guest-nights:

| | 2019 | 2024 | change | platform growth 19–24 | hotel growth 19–24 |
|---|---|---|---|---|---|
| **EU27** | 21.6% | **31.0%** | +9.4pts | +66.8% | +2.3% |
| **France** | 31.2% | **47.3%** | +16.1pts | +93.4% | −2.2% |
| Portugal | 34.1% | 40.7% | +6.6pts | +44.5% | +9.1% |
| Spain | 23.5% | 32.0% | +8.4pts | +61.5% | +5.9% |
| Italy | 21.3% | 30.9% | +9.6pts | +66.7% | +1.1% |
| Germany | 10.8% | 16.8% | +5.9pts | +62.3% | −2.2% |
| **Netherlands** | 14.7% | **14.9%** | **+0.2pts** | **+19.7%** | +18.2% |

Airbnb took nine points of European share in five years while hotel nights went nowhere. **That is a
long thesis.** It is a company compounding share against a structurally stagnant incumbent, and it is
the single strongest bull fact in this repo. Any short that puts this slide up loses the room.

The only short-usable reading is the **Netherlands row** — when share stops moving, platform growth
collapses to category growth (19.7% vs the hotel's 18.2% over five years, a dead heat) — plus France
at 47.3% having limited headroom, and regulation concentrated in the highest-share cities (Barcelona
2028, Paris/Amsterdam caps, NYC LL18). But that is a **multi-year terminal-value argument on one
country**, and this is a two-quarter pitch. **It does not belong in a Q3/Q4 short.** Leave it out;
if asked in Q&A, concede the share gain is real and pivot to the lap.

Same verdict on the party-size slide (Airbnb ~6% of solo lodging demand vs ~31% of 5+ parties,
confirmed in four datasets): interesting, not a catalyst, and not in the model — the switch-rate
machinery moved 2030 nights by 2.1% across its entire plausible range.


### Leg 7 — the macro that actually applies  [NEW, and it is the transmission channel for Leg 4]

Built and reproducible: `analysis/src/macro_short_legs_q3q4.py`.

**First, the screening result that reframes the whole pitch.** Regressing the 1-day excess return on
the beat-vs-consensus and the guide (`abnb_reaction_regression.csv`, n=18): **R² 0.052, adjusted R²
−0.074, beat coefficient p = 0.35.** Every specification has a *negative* adjusted R² and nothing
clears p = 0.35. A short built on "they miss nights by two points" has **no measured historical link
to this stock moving.** That is not an argument against the nights work — it is an argument that the
macro and valuation legs are where the edge is, not decoration on top of it.

**Second, macro is the biggest single driver of big moves, but ABNB has no macro of its own.** Of 41
daily moves ≥7% since the IPO, **20 were macro/market** — the largest bucket. On those days
**ABNB = 1.79 × QQQ, corr 0.88, 2.4× amplification in absolute terms.** It is a high-beta expression
of the tape. And the regime matters: **14 of the 20 were the 2022 hiking cycle, 2 were the April 2025
tariff days, and there were zero in 2023, 2024 or 2026.** A 7% macro day needs a macro *shock*, not a
macro drift. Do not pitch "macro is weak" and expect it to do work.

**Third, the screen — Aug 2026 vs Aug 2025:**

| channel | Aug-25 | Aug-26 | YoY | direction |
|---|---|---|---|---|
| **Fed funds** | 4.33 | 3.63 | **−16.2%** | SHORT |
| **10-year** | 4.26 | 4.68 | **+9.9%** | SHORT |
| WTI crude | 64.86 | 83.90 | +29.4% | SHORT |
| U. Mich sentiment (Jul) | 61.7 | 55.2 | −10.5% | SHORT |
| Broad dollar | 120.58 | 118.85 | −1.4% | **LONG** |
| Unemployment | 4.30 | 4.10 | −4.7% | **LONG** |

**The split is the point. The front end is 70bp lower YoY while the long end is 42bp higher.** Those
are two different variables pointing the same way for a short: the front end hits the P&L *now*, the
long end hits the multiple *now*. Against the short, and kept on the record: the dollar is 1.4%
weaker (~58% of revenue is ex-NA, so this is a real translation tailwind) and unemployment is 20bp
lower. Neither is large.

**Fourth, the one macro channel that is ABNB-specific and that nobody models — interest income.**

- FY2025 operating income **$2,544mm**; FY2025 interest income **$705mm** = **27.7% of operating income, 21.7% of pre-tax.** It is ~100% margin.
- FY23 $721mm → FY24 $818mm → **FY25 $705mm**. 1H26 $338mm vs 1H25 $363mm, **−6.9%** — *while GBV grew 16–19%.*

Two forces, same direction, both live in 3Q/4Q26: **(a)** the front end is 70bp lower so the yield on
the float falls, and **(b)** RNPL removes the float itself (unearned fees −$442mm / −$466mm below
seasonal-normal in 1Q26/2Q26, against ±5% before). 2H25 interest income was $342mm; at the 1H26 run
rate 2H26 is ~$318mm, at rate-plus-float compounding ~$301mm (−$41mm), bear ~$280mm (−$62mm).

*Honest sizing:* −$41mm is ~2% of 2H operating income. **It does not carry a short on its own.** What
it does is make Leg 4 quantitative and give it a macro tailwind, and it is one of the very few ABNB
lines whose direction is known before the print.

**Fifth, and this is where macro actually bites — the discount rate against a priced-for-growth FCF line.**

Price $181.94, EV $99.0bn, LTM FCF $4,827mm → **EV/FCF 20.5×**. But **SBC is $1,696mm, 35% of reported
FCF**; on SBC-adjusted FCF of $3,131mm it is **31.6×**. Reverse DCF, implied 10-year FCF growth:

| WACC | on reported FCF (3% TG) | on SBC-adjusted FCF (3% TG) |
|---|---|---|
| 9% | 5.3% | **11.0%** |
| 10% | 7.5% | **13.3%** |
| 11% | 9.5% | **15.5%** |

**At a 9–10% WACC the market is paying for 11–13% SBC-adjusted FCF growth for a decade** — in a cash
flow line that RNPL is structurally shrinking (float) and that falling front-end rates are shrinking
again (interest income), while the long end raises the bar to clear. That is the construction:
**macro is not a separate leg, it is the transmission channel for Leg 4.**

*What kills it:* the Fed cuts hard into a soft landing, the long end falls with it, and a
high-beta travel name re-rates up. Rate cuts are ambiguous here — bad for interest income, good
for the multiple, and the multiple is the bigger number.

## 3. What would kill this

1. They beat the guide again. They have, twice, by 3–4 points.
2. The July 2026 RNPL eligibility expansion is larger than the +0.10 to +0.30pts assumed — it is
   disclosed but never quantified, and it is the largest unquantified offset on the record.
3. Drive-to substitution offsets the air-traffic weakness (Orlando and Miami already show it).
4. The US partial-lap correction (0 to +0.34pts) cuts against the short; the 3Q25 call says
   "beginning of Q3" while the newsroom announcement is 14 August 2025.

## 4. Files

- `analysis/src/nights_short_q3q4.py` → `data/processed/nights_short_q3q4.csv`
- deleted: `analysis/src/nights_simple.py`, `data/processed/nights_simple.csv`
