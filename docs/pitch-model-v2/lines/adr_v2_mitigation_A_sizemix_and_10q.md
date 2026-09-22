# ADR line v2, mitigation A — the size-mix sign, and the 1Q26 10-Q

**22 September 2026.** Two of the five weaknesses listed in [`adr_v2_thesis.md`](adr_v2_thesis.md) §"Why the same
analyst would call it weak" are settled here, and both are settled against filings rather than against another
model. **(1)** The 0.99pp sign disagreement between the 10-K annual route's 2025 unit-size term (−0.251pp) and the
H route's (+0.739pp), flagged as open item (1) of
[`adr_v2_upgrade3_reconciliation.md`](adr_v2_upgrade3_reconciliation.md) §RESUME and called there "the single most
fragile number in the annual chain". **(2)** The one filing X3 never read —
[`dossiers/X3_x3_bundle_sentences_provenance.md`](../dossiers/X3_x3_bundle_sentences_provenance.md) §8's open
lead, the 1Q26 10-Q, accession **0001559720-26-000014**.

Engine: `analysis/src/pitch_model_v2/adr_engine/sizemix_adjudication.py`.
Outputs: `data/processed/pitch_model_v2/adr_engine/sizemix_routes.csv`, `sizemix_rebased_plug.csv`,
`sizemix_10q_sentences.csv`. Raw filing: `data/raw/regulatory/quantification/abnb_2026q1_10q.html`.

```
cd ~/Citadel-ABNB && PYTHONPATH=analysis/src python3 -W ignore -m pitch_model_v2.adr_engine.sizemix_adjudication
# exit 0; prints all five blocks and writes the three CSVs. --fetch re-pulls the 1Q26 10-Q from EDGAR.
```

Web: **two EDGAR fetches** (the filing index at
`https://www.sec.gov/Archives/edgar/data/1559720/000155972026000014/`, then the primary document
`abnb-20260331.htm`), User-Agent `Citadel-ABNB-research theobmachado@gmail.com`. No other host. Nothing in this
file is fitted: every coefficient is read from a committed file, and the only new arithmetic is a re-weighting of
an existing panel and a multiplication of a filed growth rate by a measured elasticity.

---

## 0. Verdict in five lines

1. **The 10-K route's 2025 size term is wrong, and it is wrong for a reason that can be shown rather than argued.**
   All eleven of its own eligible 2025 pairs have a **positive** size wedge (+0.39 to +3.15pp). The aggregate is
   −0.79pp only because `05_size_mix.agg()` pools nights across markets on both sides, so the change in each
   market's **share of the Inside Airbnb panel** — scrape coverage, not Airbnb nights — rides into the term.
2. **The mechanism is Paris.** Paris's panel nights grew **+43.3% y/y** in the 2025 pairs against a panel total of
   +26.6% (Airbnb's own 2025 nights grew 8.3%), lifting Paris from **51.2% to 58.0%** of panel nights. Paris is the
   panel's smallest unit (1.33 bedrooms per booked night against a base-weighted 1.47). That reweighting takes
   **−0.0269 bedrooms** out of the pooled measure against a within-market gain of **+0.0177** — three times the
   real signal, opposite sign.
3. **Held at base-period weights, the 05 route's own 2025 pairs give +0.912pp, against the H route's +0.739pp.**
   The two routes are then **0.17pp apart with the same sign**, not 0.99pp apart with opposite signs. On 2024 (one
   market, no cross-market term) pooled and fixed-weight are identical; on 2026 (12 markets, coverage roughly flat)
   they differ by 0.14pp. **2025 is the only year the defect bites, and it is the year the decomposition quotes.**
4. **The filed arbiter is positive and it brackets both routes.** The 2Q26 letter's Bedroom Nights Booked
   ("grew over 12%") against Nights and Seats Booked (+10%) is +1.80 log-pp of bedrooms per booked night; at the
   measured bedroom elasticity **0.2312** that is **+0.42pp of ADR** (+0.27 at 0.15, +0.54 at 0.30), and priced
   through the full hedonic **+1.29pp**. Every route's 2Q26 read sits inside [+0.42, +1.29]: H +0.70, the
   29-market panel +0.63, the 12-market panel +0.89. **Nothing filed supports a negative size term in any period.**
5. **Adopt the H route for the annual decomposition. 2025's implied like-for-like price is then flat, not
   accelerating: 2.68 (H size and LOS), 2.93 (H size only) or 2.76 (05 reweighted) against 2024's 2.69 / 2.75 /
   3.15 — against the 3.93 that the filed 07 term produces.** The 2025 acceleration was the artefact, not a price
   event, and it should never reach the memo.

---

## A. The two routes, reproduced from their committed files

Both routes price the same hedonic — `06_wtp_hedonic_coefs.csv`, quote basis, **bedrooms 0.1402, log capacity
0.3991** — so *the disagreement is not a price basis, a currency or a window convention. It is entirely in the
measured size shift.*

| | **10-K annual route (05 → 07)** | **H route (13 → H)** |
|---|---|---|
| Object measured | bedrooms and capacity per **booked night**, from listing dumps | **booked capacity per reviewed stay** (`accommodates` of the listing behind each review) |
| Source | Inside Airbnb listing dumps, repo tree only | Inside Airbnb **reviews** dumps |
| Panel, 2025 | **11 pairs, 4 markets** (austin, nashville, paris, rome) | **123 markets**, 15.1m reviews in the year |
| Window | `date_b` in the calendar year; pairs 335–395 days apart | calendar quarters, y/y on log capacity, four quarters GBV-weighted |
| Within-market weight | `estimated_occupancy_l365d` (estimated nights booked) | reviews |
| **Across-market weight** | **panel nights in each period** — moves with scrape coverage | **fixed 2019 share of reviews** — cannot move with coverage |
| Conversion to ADR | `exp(0.1402·Δbedrooms + 0.3991·Δln capacity) − 1`, both measured | `0.592 × Δln capacity`, where 0.592 = 0.3991 + 0.1402 × **1.374** bedrooms per unit log capacity |
| Price basis | quote basis (2026 dumps) | same |

### A.1 Side by side, pp of ADR y/y

| year | 05/07 as filed | 05 pairs, **fixed base weights** | H route | H − 07 | 07 panel |
|---|---|---|---|---|---|
| 2023 | **0.000** (not measured) | — (no eligible pair with `date_b` in 2023) | **+0.387** | +0.387 | none; 07 fills 0.0 and the term falls into the plug |
| 2024 | **+0.441** | +0.445 | **+0.841** | +0.400 | 3 pairs, **1 market** (rome) |
| 2025 | **−0.251** | **+0.912** | **+0.739** | **+0.991** | 11 pairs, 4 markets |
| 2026 | +0.872 | +1.009 | n/a (H stops 2Q26) | — | 51 pairs, 12 markets |

### A.2 What the pooled aggregation does, year by year

`05_size_mix.agg()` forms `d_bedrooms = Σ bedroom-nights_b / Σ nights_b − Σ bedroom-nights_a / Σ nights_a` and
`d_mean_log_capacity` as a period-b weighted mean less a period-a weighted mean. Both carry the change in market
shares. Decomposing the pooled `d_bedrooms` into a within-market part (base weights) and a between-market part:

| year | pairs | markets | pooled wedge | fixed-weight wedge | equal-weight wedge | within `d_bed` | **between `d_bed`** | all pairs positive? | panel nights y/y |
|---|---|---|---|---|---|---|---|---|---|
| 2024 | 3 | 1 | +0.874 | +0.878 | +0.873 | +0.0106 | **−0.0001** | yes | +21.5% |
| 2025 | 11 | 4 | **−0.795** | **+1.445** | +1.499 | +0.0177 | **−0.0269** | **yes, all 11** | **+26.6%** |
| 2026 | 51 | 12 | +1.256 | +1.451 | +1.592 | +0.0253 | **−0.0044** | no (4 of 51 negative) | −0.4% |

The 2025 market weights (base → current share of panel nights, and each market's bedrooms per booked night):

| market | weight base | weight current | Δ weight | bedrooms/night | panel nights y/y |
|---|---|---|---|---|---|
| **paris** | 51.2% | **58.0%** | **+6.77pp** | **1.327** (lowest) | **+43.3%** |
| rome | 38.2% | 33.8% | −4.44pp | 1.478 | +12.0% |
| nashville | 7.0% | 5.6% | −1.46pp | 2.221 | +0.3% |
| austin | 3.6% | 2.7% | −0.88pp | 2.063 | −4.7% |

Paris's +43% is Inside Airbnb's Paris coverage, not Airbnb's Paris nights; the repo's own `05_size_mix.py`
docstring says the wedge survives partial scope *because it is a ratio of growth rates within a market* — which is
exactly the property the cross-market pooling destroys. The defect is real but narrow: it needs several markets,
divergent coverage drift and a wide spread of unit sizes, and 2025 is the only year in the panel that has all
three.

### A.3 Where the two routes can be compared on a wide panel, they agree

`13_party_size_adr_checks.csv` rows 0–3, the 2Q26 window, capacity y/y in per cent, reviews route against the
29-market listing panel: **NA 2.44 vs 2.24, EMEA 0.57 vs 1.77, LatAm 0.01 vs 0.68, APAC 1.34 vs 0.78.** Same sign
in all four regions, same ordering (NA fastest, LatAm slowest). `I4_party_size_series_check.csv` adds that the H
series is 13's exactly (max diff 0.000pp) and that a refresh on the August-2026 dumps reproduces it on 3Q23–2Q26
at **r 0.97, RMSE 0.062pp**. The routes disagree only where the listing panel is four markets wide.

---

## B. The arbiter: what the filings imply

### B.1 The bedroom elasticity, reproduced

Krish's 2026-09-07 note states a bedroom elasticity of **0.23**, "stable across both panels (0.2289 on 12 urban
markets, 0.2312 on 29)". In a semi-log hedonic `log p = … + b_bed · bedrooms`, the elasticity of price to bedroom
*count* at a mean of B bedrooms per booked night is `b_bed × B`:

| panel | markets | pairs | bedrooms per booked night | b_bed | **elasticity** |
|---|---|---|---|---|---|
| 12-market (05, `disclosure_window_2Q26`) | 12 | 39 | 1.6324 | 0.1402 | **0.2289** |
| 29-market (08, `2Q26_panel_extended`) | 29 | 87 | 1.6489 | 0.1402 | **0.2312** |

Reproduced to four decimals. The number is not fitted here; it falls out of a committed coefficient and a
committed panel mean.

### B.2 2Q26: the only filed size metric

The 2Q26 shareholder letter (8-K Ex 99.1, `02_kpi_panel_long.csv` row `2Q26,bedroom_nights_yoy_pct`):
*"Bedroom Nights Booked — nights booked multiplied by bedroom count — grew over 12%"*, against Nights and Seats
Booked **+10%**, with *"more than 1 billion bedroom nights over the trailing twelve months, a record"*.

Bedrooms per booked night therefore grew `ln(1.12) − ln(1.10) = +1.802%` — and "over 12%" makes that a **floor**.

| mapping | ADR contribution, 2Q26 |
|---|---|
| bedroom channel only, ε = 0.2312 (29 markets) | **+0.417pp** |
| bedroom channel only, ε = 0.2289 (12 markets) | +0.412pp |
| bedroom channel only, ε = 0.15 | +0.270pp |
| bedroom channel only, ε = 0.30 | +0.541pp |
| **full hedonic** (bedrooms + the capacity that moves with them at 1.374 bedrooms per unit log capacity) | **+1.288pp** |

The bracket is **[+0.42pp, +1.29pp]**, and the second number is the mapping both routes actually use, so it is the
like-for-like comparator. The three measured 2Q26 reads:

| route | 2Q26 capacity y/y | 2Q26 size term | inside the bracket? |
|---|---|---|---|
| H route (reviews, 119–123 markets) | +1.184% | **+0.700pp** | yes |
| 08 extended listing panel (29 markets, 87 pairs) | +1.205% | **+0.626pp** | yes |
| 05 listing panel (12 markets, 39 pairs) | +1.629% | **+0.886pp** | yes |

**No filed number is consistent with a negative size term.** That is the whole arbiter, and it is one-sided.

### B.3 2025: the filings do not give a size read, and it is worth saying why

Asked of the FY2025 10-K directly (`abnb_2025_10k.json`, full text): **"bedroom" appears exactly once**, and it is
definitional — *"A night can include one or more guests and can be for a listing with one or more bedrooms."*
There is no bedroom-nights figure, no guests-per-booking figure ("guests per" returns zero hits), and the Bedroom
Nights Booked metric does not start until 2Q26. **The 10-K therefore carries no 2025 size arbiter, and none can be
constructed from it.** The 2Q26 letter's TTM statement ("more than 1 billion bedroom nights over the trailing
twelve months") covers 3Q25–2Q26 and so overlaps FY2025 by two quarters, but it is a level, not a growth rate, and
it cannot be split.

**Nights per booking is a length-of-stay metric, not a size metric**, and it should not be pressed into service as
one. What it does arbitrate is the *other* term the two routes disagree about. The FY2025 10-K: *"Our total
Company average nights per booking, excluding experiences and services, was 3.7 in 2025 compared to 3.8 in 2024.
Average nights per booking in 2025 was 4.1 for North America, 3.8 for EMEA, 3.6 for Latin America, and 3.3 for
Asia Pacific."* That is −2.63%. Holding each region's own 2025 nights per booking fixed and moving only the
regional nights weights reproduces just **−0.012 of the −0.100 night decline (12%)**, so ~88% is a genuine
within-region shortening. At the externally bounded LOS elasticity −0.15 (band −0.05 to −0.25, `adr_v1_design`
§4.4, not fitted) that implies **+0.40pp of ADR (band +0.13 to +0.67)** — which contains the H route's **+0.291**
and sits well above 07's **+0.036**. **Caveat, stated:** the 10-K rounds nights per booking to 0.1, so 3.8 → 3.7
is −2.63% ± ~1.3pp and the low end of that rounding band does not exclude 07's number. This leg is corroboration,
not proof; the bedroom leg is the decisive one.

---

## C. The verdict, and what it does to the plug

### C.1 The annual decomposition should carry the H route

Six reasons, in descending order of weight.

1. **The 05 route's own pairs agree with H once the coverage drift is removed** (+0.912 against +0.739, 0.17pp).
   The disagreement is not between two measurements of the world; it is between one measurement and an aggregation
   artefact laid on top of it.
2. **Every one of the 11 eligible 2025 pairs is positive.** A term that contradicts all of its own inputs is not a
   finding.
3. **The only filed size metric is positive**, and its bracket contains every route's 2Q26 read (§B.2).
4. **Panel**: 123 markets and ~15.1m reviews against 4 markets and 11 dump pairs. Inside Airbnb's coverage of
   Paris and Rome in 2024–25 is not a global size panel and was never claimed to be.
5. **Weighting**: fixed 2019 market weights are immune by construction to the defect in §A.2 — the same reason
   `13_party_size_adr.py`'s docstring gives for choosing them ("so Inside Airbnb adding cities cannot masquerade
   as a trend").
6. **Reproducibility**: the H series reproduces on refreshed dumps at r 0.97 / RMSE 0.062pp and matches the wide
   listing panel region by region at 2Q26.

**What adopting H costs, stated.** H does not measure bedrooms; it imposes `Δbedrooms = 1.374 × Δln capacity` from
the 29-market panel, so it cannot see a bedrooms-versus-capacity divergence. It is review-based and therefore
survivor-biased (I's vintage-matched versus within-vintage reads differ by 0.03pp, so this is second order). And
it has **no forecast content**: `I4_backtest_scoreboard.csv` gives r −0.17 against ex-FX ADR at lead 0 and a
walk-forward ratio of 4.17 against naive — it is a level term and must stay labelled one. None of these three
bears on the 2025 sign, which is the only question here.

### C.2 The rebased plug (`sizemix_rebased_plug.csv`)

`plug = within-region ex-FX − size − LOS` (`07_assemble.py` line 103); `implied like-for-like price = plug − our
sub-regional mix` (`reconcile.py`, sub-geo −0.860 / −0.357 / −0.304).

| variant | size 2023/24/25 | LOS 2023/24/25 | **implied like-for-like price 2023 / 2024 / 2025** | 2025 − 2024 |
|---|---|---|---|---|
| **A** as filed (05 pooled, 03 LOS) | 0.000 / 0.441 / −0.251 | 0.617 / 0.205 / 0.036 | **3.339 / 3.154 / 3.925** | **+0.771** |
| **B** adopted H size, 03 LOS | 0.387 / 0.841 / 0.739 | 0.617 / 0.205 / 0.036 | **2.953 / 2.754 / 2.934** | +0.180 |
| **C** adopted H size **and** H LOS | 0.387 / 0.841 / 0.739 | 0.312 / 0.274 / 0.291 | **3.258 / 2.685 / 2.679** | **−0.006** |
| **D** 05 pairs reweighted, 03 LOS | — / 0.445 / 0.912 | 0.617 / 0.205 / 0.036 | — / 3.149 / **2.761** | −0.388 |

**Answer to the question the brief asks: 2025's like-for-like price is FLAT (2.68–2.93), not accelerating (3.93).**
The result does not depend on whether the LOS term is swapped as well — B, C and D all remove the step, and D does
it using nothing but the 10-K route's own pairs. The +0.77pp "2025 acceleration" in the filed decomposition is
**0.99pp of size-mix artefact partly offset by 0.26pp of LOS**, and it is not a price event.

Against the GBV-weighted accommodation-CPI blend (7.10 / 2.37 / 1.51), the 2025 gap the reconciliation note names
as the line's exposure narrows from **+2.42pp to +1.17pp (C) / +1.43pp (B) / +1.26pp (D)**. The exposure survives —
the implied price still runs above every accommodation index in 2024 and 2025, and the gap still widens from 2024 —
but it is about **half** the size the filed decomposition implies, and the 2023 → 2025 path becomes a plateau
rather than a ramp.

---

## D. The 1Q26 10-Q

**Accession 0001559720-26-000014**, primary document `abnb-20260331.htm`, filed **2026-05-07** (the same day as the
1Q26 earnings call that carries D032's "~3 pts nights / ~4 pts GBV"). Fetched from EDGAR in two requests and saved
verbatim to `data/raw/regulatory/quantification/abnb_2026q1_10q.html` (1,123,584 bytes).

### D.1 Term counts, 1Q26 against 2Q26

| term | **1Q26 10-Q** | 2Q26 10-Q |
|---|---|---|
| "basis points" | **0** | 0 |
| "points of" | **0** | 0 |
| **"RNPL"** | **0** | **8** |
| **"Reserve Now"** | **0** | 1 |
| "Pay Later" | **0** | 1 |
| "flexible payment" | **0** | 4 |
| **"deferred payment"** | **3** | 0 |
| "single fee" | **0** | 0 |
| "mix shift" | **0** | 0 |
| "cancellation" | 6 | 6 |
| "service fee" | 2 | 2 |
| "simplif" | 3 (all FASB ASU boilerplate) | 3 |
| "average daily rate" / "ADR" | 2 / 4 | 2 / 6 |
| "constant currency" | 6 | 7 |

**The headline finding is the zero.** The 1Q26 10-Q never names RNPL, Reserve Now, Pay Later or flexible payments
anywhere in the document. It refers to the same thing three times as *"our deferred payment programs"*. The first
filed naming of RNPL is the 2Q26 10-Q.

The one "basis point" hit in the 1Q26 filing is a **verified false positive**: *"An immediate hypothetical 100
basis point increase or decrease in market interest rates would result in an estimated change of $17 million in
our annualized interest expense"* — Item 3, interest-rate risk on the senior notes and the $1.7bn of swaps.
Nothing to do with the bundle.

### D.2 Every sentence naming the programme, the fee change or the cancellation policy as a driver — verbatim

**1Q26 10-Q, Item 2 MD&A → Key Business Metrics and Non-GAAP Financial Measures → Nights and Seats Booked:**

> "During the three months ended March 31, 2026, the increase in Nights and Seats Booked, compared to the same
> period in the prior year, was driven by growth across all regions despite increased cancellations in EMEA and
> Asia Pacific from the Middle East conflict, with the strongest growth percentages in Latin America and Asia
> Pacific, as we continue to focus on international expansion."

> "In addition, we observed a lengthening of lead times across all regions, driven in part by the continued
> expansion of our deferred payment programs."

**1Q26 10-Q, MD&A → Gross Booking Value:**

> "The entire amount of a booking is reflected in GBV during the quarter in which booking occurs, whether the
> guest pays the entire amount of the booking upfront or elects to use our deferred payment programs."

> "During the three months ended March 31, 2026, the increase in GBV, compared to the same period in the prior
> year, was primarily due to an increase in Nights and Seats Booked and ADR. We saw GBV growth across all regions,
> with the strongest growth percentages in Latin America and Asia Pacific."

**1Q26 10-Q, MD&A → Liquidity and Capital Resources → Cash Flows:**

> "The growth in GBV was driven in part by increased guest adoption of our deferred payment programs, which allows
> guests to pay closer to check-in dates rather than at time of booking, which shifts the timing of when net cash
> provided by operating activities is recognized."

> "For example, while our GBV increased during the three months ended March 31, 2026 compared to the same period
> in the prior year, our unearned fees remained relatively flat primarily, reflecting the shift in payment timing
> associated with the increased adoption of these programs."

**1Q26 10-Q, MD&A → Macroeconomic and Geopolitical Conditions on our Business:**

> "The conflict in the Middle East has had and is expected to continue to have a slight impact on near-term
> booking trends, including increased cancellations in Europe, the Middle East, and Africa ("EMEA") and Asia
> Pacific."

**All six of the 1Q26 filing's "cancellation" hits are either this Middle East sentence, the Nights sentence above,
or the standing definitional language** ("net of cancellations and alterations"; "If, in the example, the booking
were canceled on May 15…"). **The October-2025 cancellation-policy redesign is not mentioned, and neither is the
single fee.**

### D.3 Is any magnitude filed? **No.**

Across both 10-Qs, **15 sentences name RNPL, Reserve Now, Pay Later, deferred payments or flexible payments. None
of them contains a number of any kind** — no basis points, no points, no percentages, no dollar amounts
(`sizemix_10q_sentences.csv`, `magnitude_filed` is "no" on all 39 rows; the `any_number_in_sentence` column shows
the six numeric sentences in the file are all revenue and cost-of-revenue growth rates in sentences that name no
product).

### D.4 The matched pair, 1Q26 against 2Q26

The two filings put the same sentence in the same place. The 2Q26 one has a clause the 1Q26 one does not:

| | 1Q26 10-Q, §Gross Booking Value | 2Q26 10-Q, §Gross Booking Value |
|---|---|---|
| GBV driver | "…was primarily due to an increase in Nights and Seats Booked and ADR. We saw GBV growth across all regions, with the strongest growth percentages in Latin America and Asia Pacific." | "…was primarily due to an increase in Nights and Seats Booked and ADR. We saw GBV growth across all regions, led by Latin America and Asia Pacific, with North America and EMEA growing more moderately." |
| next sentence | *(none — the paragraph ends)* | **"The increase in ADR was driven in part by the continued adoption of RNPL."** |
| financial highlights | "…and an increase in our Average Daily Rate ("ADR")." | "…and a **modest** increase in our Average Daily Rate ("ADR")." |
| RNPL risk language | **absent** | "To date, RNPL bookings, which require no payment at the time of booking, have experienced higher cancellation rates than historic bookings in which some or all of the cash was received at the time of booking." |

So the **ADR** attribution to the bundle is filed exactly once, in the 2Q26 10-Q, qualitatively. The **GBV**
attribution is filed twice — 1Q26 ("The growth in GBV was driven in part by increased guest adoption of our
deferred payment programs") and 2Q26 — also qualitatively. The **nights** attribution is filed once, obliquely,
in 2Q26 ("We also continued to benefit from our product initiatives, including improvements to search and
merchandising, pricing and tools, and flexible payment options"). **The magnitudes are filed nowhere.**

### D.5 What this does to X3

X3's §8 open lead is **closed, and its conclusion is confirmed and slightly strengthened**. The `mirror` flag on
ledger rows D014 (4Q25, 2.0 nights / 3.0 GBV points) and D032 (1Q26, 3.0 / 4.0) **stands**; a follow-up digger run
on the 1Q26 10-Q is no longer needed and should be struck from the to-do list. Two things are *new* relative to
X3's table:

- **A filed GBV attribution exists for 1Q26** after all — in Liquidity, not in the driver MD&A, and naming
  "deferred payment programs" rather than RNPL. X3 could not see it because the fetch budget ran out. The memo can
  now say the qualitative attribution is filed for GBV in **both** 1Q26 and 2Q26 and for ADR in 2Q26, and that
  only the magnitude is transcript-only. That is a slightly better sentence than the one X3 left us.
- **The company did not name RNPL in a filing until 2Q26**, one quarter after the call that sized it at 3–4 points.
  That is worth one line in the memo on its own: the disclosure asymmetry between the call and the filing is not
  our inference, it is on the face of the two documents.

---

## E. What changes in the thesis

| claim | before | after |
|---|---|---|
| `adr_v2_thesis.md` weakness 4: "the 10-K annual route and the H route disagree on the 2025 size-mix sign by a full point" | open | **closed.** The 10-K route's 2025 term is a cross-market weighting artefact; rebuilt on its own pairs at fixed base weights it is +0.912 against H's +0.739. **Adopt H (DEC proposed below).** |
| `adr_v2_upgrade3_reconciliation.md` §C bullet 3: "on our own size/LOS terms, like-for-like price is flat at 2.69 / 2.68 in 2024-25 … the single most fragile number in the annual chain" | flagged as fragile, both numbers carried | **the rebased column is now the primary.** 2025 like-for-like price is **2.68–2.93**, flat against 2024; the 3.93 is withdrawn. Tables A.2 and A.4 of that note should be read with variant C. |
| `adr_v2_thesis.md` weakness 2: "the bundle's one point of ADR is transcript-only; no filing carries it" | open, with one filing unread | **label KEPT, and now exhaustive.** Every SEC filing that could carry the magnitude has been read: FY25 10-K, 1Q26 10-Q, 2Q26 10-Q, and the two 8-K Ex 99.1 letters (X3). Zero magnitudes. The qualitative attribution is filed for GBV (1Q26 and 2Q26) and for ADR (2Q26 only). |
| The 2026 core step (§3.1's 1.45pp) | unexplained, and made to look larger by a spurious 2025 base | **unchanged in 2026, but its base is now flat.** With 2025 at 2.68–2.93 rather than 3.93, the 2026 core step measured off 2025 is *larger*, not smaller — the thesis's own exposure is honestly bigger on this point, and the memo should say so rather than bank the 0.99pp. |
| The price-versus-CPI gap | +2.42pp in 2025 | **+1.17 to +1.43pp.** Still positive, still widening from 2024, about half the size. |

**Proposed decision, pending Theo. DEC-0040:** `07_full_decomposition.csv`'s `size_mix_pp` is superseded by the H
route for the annual decomposition (2023 +0.387, 2024 +0.841, 2025 +0.739); 07 is *not* edited (other agents hold
it), the override lives in `sizemix_rebased_plug.csv` variant C and any workbook cell that quotes the annual plug
should read from there. **DEC-0041:** the "transcript-only" label on the bundle's ~1pp stays on every slide and
sentence that uses the 2.0/3.0 and 3.0/4.0 points, with the filed qualitative sentence quoted alongside it
(X3 §8 recommendation (c)); the 1Q26 10-Q follow-up is closed.

---

## RESUME

`sizemix_adjudication.py` runs both blocks end to end and exits 0; `sizemix_routes.csv` (21 rows: both routes, the
reweighted 05 pairs, the filed decomposition as it stands, and the two filed arbiters), `sizemix_rebased_plug.csv`
(12 rows: four size/LOS variants × three years) and `sizemix_10q_sentences.csv` (39 rows across the two 10-Qs,
with `section`, `magnitude_filed`, `names_rnpl`, `is_driver_claim`) hold every number and every quote above.
**Two things were decided.** The annual decomposition should carry the H route's size term, because the 10-K
route's 2025 number contradicts all eleven of its own pairs and is produced by a cross-market pooling that Paris's
+43% scrape-coverage growth turns into a 1pp error; and the bundle's magnitude stays labelled transcript-only,
because the last unread filing turns out not to name RNPL at all. **Three things are open.** (1) The H route
imposes bedrooms ∝ log capacity at 1.374 and cannot see a divergence between the two channels — the 05 panel could
test that directly if it is rebuilt with fixed base weights as a committed output rather than a recomputation here,
which is a one-function change in `05_size_mix.agg()` and should be raised with whoever owns `analysis/src/adr/`.
(2) The 2023 size term is still 0.000 in the filed decomposition and +0.387 on H; the plug for 2023 is therefore
0.39pp too large as filed, which nothing in the memo currently depends on but which should not be quoted. (3) The
nights-per-booking arbiter for the LOS term is suggestive only, because the 10-K rounds to 0.1 night; if a LOS
number is wanted for the memo it should be H's +0.291 with the rounding caveat, not 07's +0.036 and not a fitted
elasticity. **Do not re-litigate the size sign with another panel.** The question is settled by the 05 route's own
pairs plus one filed metric, and a third panel would only add a third weighting convention to argue about.
