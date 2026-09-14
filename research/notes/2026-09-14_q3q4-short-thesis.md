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

**Three independent nowcasts agree, and none of them is my model.**

| method | 3Q26 nights YoY | file |
|---|---|---|
| NTTO overseas inbound QTD (best walk-forward feature, ratio 0.74 vs naive) | **+9.17%** | `q3nowcast/G/G_nowcast_3q26_observable.csv` |
| NTTO Western Europe QTD | +9.40% | same |
| TSA QTD-72 | +7.45% | same |
| Inside Airbnb review index, equal / median weighted | +9.20 / +9.23% | `q3nowcast/E_aug/q3_2026_nowcast.csv` |
| this overlay | +8.86% | `nights_short_q3q4.csv` |
| naive carry-forward | 10.34% | — |
| **guide midpoint** | **11%** | — |

The leading external feature is reading **NTTO overseas inbound at −7.0% YoY** and **Western Europe
inbound at −10.5%**. US inbound travel is contracting while the guide assumes low double-digit
nights growth. Only the CPI-lodging features print above the guide (11.9%), and they are the
weakest of the set on walk-forward.

**Counterweight, and it decides the trade structure:** Airbnb has **beaten the top of its own
nights range both times it gave one** — 4Q25 guided 4–6%, printed 9.82%; 1Q26 guided 7–9%, printed
9.15%. A short that needs them to miss a guide they habitually beat is the wrong trade. The
February 1Q27 guide against a +17.9% comp is the better expression; these two quarters are the
setup.

## 2. Thesis legs

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

### Leg 5 — vacation destinations are rolling over  [NEW, and it is the one with clean data]

`data/processed/destination_air_vs_str_snapshot.csv` — air traffic into marquee leisure markets:

| destination | period | air traffic YoY |
|---|---|---|
| **Cancun** (ASUR CUN) | Jun 2026 | **−11.5%** |
| **Las Vegas** (Harry Reid) | Jun 2026 | **−9.3%** |
| **Japan** (JNTO inbound) | Jun 2026 | **−6.8%** |
| **Orlando** (MCO) | Jun 2026 | **−4.8%** |
| Miami (MIA) | May 2026 | +0.5% |
| Hawaii (DBEDT arrivals) | Jul 2026 | +1.2% |
| Athens | Jun 2026 | +1.7% |
| Barcelona (El Prat) | Jul 2026 | +6.0% |

Las Vegas STR **RevPAR −17.1%** and Cancun STR revenue **−7.3%** confirm it on the supply side.
Orlando and Miami diverge (occupancy/RevPAR up on falling air traffic) — that is drive-to
substitution and it is a genuine offset, kept on the record.

Cross-checked against the forward booking pace in `q3nowcast/F/F2_q3_in_progress.csv` (lead-time-
adjusted YoY listing-nights booked for Sep 2026): **Singapore −6.7pp, Mexico City −4.2pp, Tokyo
−3.9pp, Western Australia −3.8pp, Bangkok −3.4pp, Austin −7.5pp, London −7.2pp, Paris −2.2pp.**
Against that: Rio +9.7pp, Santiago +5.9pp, Chicago +5.8pp, Northern Rivers +4.8pp, Mornington
Peninsula +4.3pp, Rome +3.6pp, San Diego +3.7pp. **It is a genuine split, not a uniform rollover** —
APAC city markets and the US sunbelt are soft, LatAm and Australian coastal are strong. Pitch it as
*the soft markets are the high-ADR ones*, not as a global demand collapse.

### Leg 6 — the share-gain engine is running out of road in its best markets

`eurostat_platform_vs_hotel_by_country_2019_2024.csv`, platform STR share of commercial guest-nights:

| | 2019 | 2024 | change | platform growth 19–24 | hotel growth 19–24 |
|---|---|---|---|---|---|
| **EU27** | 21.6% | **31.0%** | +9.4pts | +66.8% | +2.3% |
| **France** | 31.2% | **47.3%** | +16.1pts | +93.4% | −2.2% |
| Portugal | 34.1% | 40.7% | +6.6pts | +44.5% | +9.1% |
| Spain | 23.5% | 32.0% | +8.4pts | +61.5% | +5.9% |
| Italy | 21.3% | 30.9% | +9.6pts | +66.7% | +1.1% |
| Germany | 10.8% | 16.8% | +5.9pts | +62.3% | −2.2% |
| **Netherlands** | 14.7% | **14.9%** | **+0.2pts** | **+19.7%** | +18.2% |

Read this honestly: for five years essentially **all** of Airbnb's European growth was share taken
from hotels, not category growth — hotel nights were flat to down everywhere. That is a bull fact
about the past. The short reading is the **Netherlands row**: once share stops moving, platform
growth collapses to category growth (19.7% vs the hotel's 18.2% over five years — a dead heat).
France is at **47.3% of all commercial guest-nights** in Airbnb's #2 market. There is not another
16 points to take, and the regulatory pressure is concentrated in exactly the highest-share cities
(Barcelona's 2028 ban, Paris and Amsterdam caps, NYC LL18). EMEA is 38.7% of revenue.

Related, and a clean pitch slide: Airbnb takes ~**6% of solo lodging demand but ~31% of 5+ party
demand** (confirmed in four independent datasets). The company's share is concentrated in the
segment that travels least often. The hotel comparison is a good *thesis* point; it is **not** in
the nights model, deliberately — the switch-rate machinery moved 2030 nights by 2.1% across its
entire plausible range, and the NA reconciliation found neither the switch rate nor the contestable
share could close the gap at *any* value.

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
