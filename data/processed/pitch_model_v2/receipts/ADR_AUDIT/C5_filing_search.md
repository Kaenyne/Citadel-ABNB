# C5 — Is the bundle's ~1pp ADR contribution really "transcript-only"? An attempt to falsify it

Date: 2026-09-22 · Auditor: adversarial subagent (Fable) · Tree: `citadel-abnb-adraudit` (detached, theo/pitch-model-v2), raw
documents read from `citadel-abnb` (gitignored) · Script: `C5_filing_search.py` · Hits: `C5_filing_hits.csv` (110 rows) ·
Term counts: `C5_term_counts.csv` · Fetch log: `C5_fetch_log.json`

Claim under test (`docs/pitch-model-v2/lines/final_adr.md` §3.4 and §9; `adr_v2_mitigation_A_sizemix_and_10q.md` §D/§E; DEC-0041):

> "This is transcript-only, and as of 22 September that label is exhaustive. Mitigation A read the FY25 10-K, the 1Q26 and
> 2Q26 10-Qs and both shareholder letters end to end. No filing carries a magnitude. Airbnb did not name RNPL in a filing at
> all until 2Q26."

## 1. Verdict

**No filed magnitude was found. The "transcript-only" label survives a wider search than the authors ran.** Ten SEC-filed
documents (five 8-K Ex 99.1 letters 2Q25–2Q26, the FY25 10-K, the 3Q25 / 1Q26 / 2Q26 10-Qs, the 2026 DEF 14A) were searched
for any number within ±2 sentences of the RNPL / cancellation / fee vocabulary. 79 filed hit rows; every number in the same
sentence as a feature name is a product parameter ($0 upfront; 3% / 15.5% fee rates), a *share* (70% adoption of eligible
bookings; ~20% of global GBV), a Brazil-specific installment share, or an unrelated KPI. Zero filed sentences state a
contribution of the bundle (or of any one of the three features) to ADR, GBV, nights or revenue growth.

**But two sentences in the claim are wrong as written and should be corrected:**

1. **"Airbnb did not name RNPL in a filing at all until 2Q26" is false.** The 3Q25 shareholder letter — 8-K Exhibit 99.1,
   filed 2025-11-06, accession 0001193125-25-269432 — names "Reserve Now, Pay Later" five times. It is true only for the
   four-letter acronym "RNPL" and only within the 10-K/10-Q series (first "RNPL" string: 2Q26 10-Q). The authors' own ledger
   row D008 quotes the 3Q25 letter naming it, so the sentence contradicts their ledger.
2. **"Both shareholder letters" means the 4Q25 and 1Q26 letters only** (X3 §2a), and X3 did not read them locally — it relied
   on a prior RNPL-keyword passage extraction (12 + 24 hits) in Theo's untracked folder. The 3Q25 and 2Q26 letters, the 3Q25
   10-Q and the DEF 14A were not searched for a magnitude. "Exhaustive" was therefore overstated; it is now true.

## 2. Documents searched — authors vs this audit

| document | SEC form | filed | authors searched for a magnitude? | C5 | names "Reserve Now, Pay Later"? | "RNPL" string? | magnitude? |
|---|---|---|---|---|---|---|---|
| 2Q25 letter `2Q25_d17531dex991.htm` | 8-K Ex 99.1 | 2025-08-06 | no | yes | no (pre-launch; "more flexible payment options") | no | no |
| 3Q25 letter `3Q25_d40503dex991.htm` | 8-K Ex 99.1 | 2025-11-06 | **no** (quoted for dates only, D008/D012) | yes | **yes, 5×** | no | no |
| 3Q25 10-Q `abnb-20250930.htm` | 10-Q | 2025-11-06 | **no** (not on disk) | **yes, fetched** | no ("Pay Less Upfront program" once) | no | no |
| FY25 10-K | 10-K | 2026-02-12 | yes | yes | yes, 2× (business description; FX-exposure list) | no | no |
| 4Q25 letter `4Q25_d58192dex991.htm` | 8-K Ex 99.1 | 2026-02-12 | yes (keyword extraction, X3) | yes | yes, 3× | no | no |
| 2026 DEF 14A `d936646ddef14a.htm` | DEF 14A | 2026-04-24 | **no** | **yes, fetched** | yes, 1× (qualitative) | no | no |
| 1Q26 letter `1Q26_d23351dex991.htm` | 8-K Ex 99.1 | 2026-05-07 | yes (keyword extraction, X3) | yes | yes, 9× | no | no (20% GBV share) |
| 1Q26 10-Q `abnb-20260331.htm` | 10-Q | 2026-05-07 | yes (Mitigation A §D) | yes | no ("deferred payment programs" 3×) | no | no |
| 2Q26 letter `2Q26_d70413dex991.htm` | 8-K Ex 99.1 | 2026-08-06 | **no** for the bundle (used for bedroom nights only) | yes | yes, 8× | no | no |
| 2Q26 10-Q `abnb-20260630.htm` | 10-Q | 2026-08-06 | yes | yes | yes, 1× | yes, 8× | no |

8-Ks Aug 2025–Aug 2026 (from the on-disk EDGAR submissions index `docs/pitch-forecasts/questions/bonus-insider-selling/sources/
sec_submissions_CIK1559720_20260917.json`, as of 2026-09-17): 2025-08-06 (2.02/9.01, 2Q25 letter), 2025-11-06 (2.02/9.01, 3Q25
letter), 2025-11-21 (5.02 officer matter), 2026-02-12 (2.02/9.01, 4Q25 letter), 2026-03-16 (1.01/2.03/8.01, financing),
2026-05-07 (2.02/9.01, 1Q26 letter), 2026-06-11 (5.07 annual-meeting vote), 2026-08-06 (2.02/9.01, 2Q26 letter). **No 8-K
announces RNPL, the cancellation redesign or the fee change**; the only product-carrying exhibits are the letters, all searched.
A DEFA14A (2026-04-24) accompanies the proxy and was not fetched (budget); the DEF 14A body itself carries no magnitude.

Term counts per document are in `C5_term_counts.csv`.

## 3. Every filed sentence that names a feature and carries a number in the same sentence (verbatim)

| doc | sentence | number | what it is |
|---|---|---|---|
| 3Q25 letter | "…we recently introduced a feature in the U.S. that gives guests the option to reserve an eligible stay and pay $0 upfront." | $0 | product parameter |
| 3Q25 letter | "In August, we launched our Reserve Now, Pay Later payment option within the U.S., which allows guests to pay $0 upfront when they book eligible domestic stays." | $0 | product parameter |
| 3Q25 letter | "Giving guests in Brazil this option [fee-free installments up to 6 months] has already accounted for nearly 50% of total bookings value in Q3." | ~50% | Brazil installments share of bookings value — not RNPL, not the bundle |
| 3Q25 letter | "We migrated property management software ("PMS") hosts on our split fee structure (where hosts paid a 3% fee and guests paid a separate service fee) to a single 15.5% single service fee." | 3%, 15.5% | fee-rate parameters |
| 4Q25 letter | "After a strong U.S. launch—with over 70% adoption by eligible bookings*—and testing in other markets, we're rolling it out to more guests in 2026." footnote: "*Adoption percentage based on global GBV in Q4 2025." | >70% | RNPL adoption share of *eligible* bookings, GBV-weighted — a share, not a contribution (ledger D022 already has it) |
| 4Q25 letter | "With Reserve Now, Pay Later, guests can book homes with $0 upfront." | $0 | product parameter |
| 4Q25 letter | "…most non-PMS hosts on our platform that were previously subject to our single fee structure are now subject to the 15.5% fee as of December." | 15.5% | fee-rate parameter |
| 1Q26 letter | "And in Q1, roughly 20% of global GBV came from Reserve Now, Pay Later bookings." | ~20% | RNPL share of GBV — a share, not a contribution (D031) |
| 1Q26 letter | "We began migrating property management software hosts from a split fee structure (where hosts paid a 3% fee and guests paid a separate service fee) to a single service fee of 15.5% for most hosts." | 3%, 15.5% | fee-rate parameters |
| 2Q26 letter | "We initially migrated most property management software hosts from a split fee structure (…3% fee…) to a single fee of 15.5%." / "In July, we announced plans to migrate most of the remaining hosts to a single 15.5% service fee…" | 3%, 15.5% | fee-rate parameters |
| 2Q26 letter | "Our FCF increased 30% year-over-year primarily due to higher net income, partially offset by working capital changes, including the impact from the continued expansion of Reserve Now, Pay Later." | 30% | FCF growth; RNPL is an unsized offset |
| 2Q26 10-Q | eight "RNPL" sentences (FCF timing, unearned fees, cancellation-rate risk, "The increase in ADR was driven in part by the continued adoption of RNPL.") | none in-sentence | qualitative |
| DEF 14A | "In 2025, we launched Airbnb Services and Experiences to expand our offerings and executed a series of product improvements that helped drive an acceleration in business performance, including Reserve Now, Pay Later, updated cancellations policies, and simplified fees." | none | qualitative; the proxy never mentions "Nights and Seats Booked", names the Stock Price Measure as its most important performance measure, and reports the Bonus Plan paid at 100% of target — no product outcome is quantified |
| 3Q25 10-Q | "…whether the guest pays the entire amount of the booking upfront or elects to use our Pay Less Upfront program." | none | RNPL not named; no product driver sentence for GBV or nights |

Qualitative filed attributions (no number) that the memo may quote: 3Q25 letter "The introduction of Reserve Now, Pay Later
helped drive the acceleration of Nights and Seats Booked in North America during Q3 2025"; 1Q26 10-Q "The growth in GBV was
driven in part by increased guest adoption of our deferred payment programs"; 2Q26 10-Q "The increase in ADR was driven in part
by the continued adoption of RNPL"; DEF 14A sentence above (the first filed document to name all three bundle features together
as drivers of "an acceleration in business performance").

## 4. The two transcript quotes, verbatim (not filings; `data/raw/transcripts/web/4Q25.html`, `1Q26.html`, stockanalysis mirror)

**4Q25 call, 2026-02-12, Ellie Mertz (CFO), prepared remarks** (speaker marker at char 13,891 precedes the sentence at 16,069):

> "In Q4, a few updates in particular helped drive our acceleration. The launch of Reserve Now, Pay Later, updates to our
> cancellation policy, and the beginning of our migration to a simplified fee structure. […] Our updated cancellation policies
> and simplified fees also contributed to both nights and GBV growth in the quarter. […] **In total, we estimate these three
> features delivered over 200 basis points of growth in nights booked and roughly 300 basis points of growth in GBV in Q4.**"

**1Q26 call, 2026-05-07, Ellie Mertz (CFO), prepared remarks** (marker at 10,749 precedes the sentence at 12,880):

> "Last quarter, I shared three initiatives in particular that help drive the continued momentum across our business. The
> broader expansion of Reserve Now, Pay Later, updates to our cancellation policies, and the migration of certain hosts to a
> simplified fee structure. First, **we expanded Reserve Now, Pay Later to more markets, and adoption continued to increase.**
> […] Over a quarter of our active listings is now subject to the single service fee. **In total, we estimate these three
> features delivered approximately three points of nights booked growth and approximately four points of GBV growth in Q1.**"

What the numbers refer to: contribution to **year-over-year growth in the quarter** (Q4 2025; Q1 2026), of the **three features
combined, globally**, in nights booked and in GBV. No ex-FX qualifier is given for the contributions (the same remarks report GBV
growth on both a reported and ex-FX basis, so the basis of the contribution is unspecified). No per-feature split on either
call or in the Q&A (D007: an analyst asked "what percentage of the acceleration in the U.S. has come from that?" on the 3Q25
call and got no figure).

**The 1Q26 figure includes the ex-North-America RNPL launch.** The sentence immediately before it is "we expanded Reserve Now,
Pay Later to more markets, and adoption continued to increase", and the 4Q25 letter says testing in additional markets was
completed in February 2026 (global availability 17 Feb 2026, D025). So ~6 weeks of the ex-NA leg sit inside the "~3 / ~4 points".
The model's §3.4 treats the ex-NA leg as "0 in the base because it has never been sized" while dating the whole 1pp to features
that lap in 3Q26/4Q26; strictly, part of the 1Q26 step belongs to a leg that laps in 1Q27. The transcripts do not let anyone
size that part.

**Rounding.** The ADR contribution is the authors' arithmetic (GBV points − nights points), not a management number. Reading
the stated roundings literally:

| call | nights | GBV | ADR gap permitted | point reading |
|---|---|---|---|---|
| 4Q25 | "over 200bp" = 2.0–2.5 (anything ≥2.5 would be "roughly 250/300") | "roughly 300bp" = 2.5–3.5 | **0.0 – 1.5pp** | 3.0 − 2.0/2.25 = 0.75–1.0 |
| 1Q26 | "approximately three" = 2.5–3.5 | "approximately four" = 3.5–4.5 | **0.0 – 2.0pp** | 4.0 − 3.0 = 1.0 |

The rounding therefore permits roughly 0–1.5pp (4Q25) and 0–2pp (1Q26); a tighter but still honest band is 0.5–1.5pp. The
model's **0.8–1.2pp band is narrower than the rounding supports** — it is a judgement band around the point reading, and should
be labelled as such, not presented as what management's rounding implies. (Because ADR ≡ GBV / nights, the GBV-minus-nights gap
is the ADR contribution to first order; the compounding error at these magnitudes is <0.1pp.)

## 5. Filed RNPL share of nights or bookings

**None.** Every filed RNPL share is GBV-denominated: "over 70% adoption by eligible bookings" with the footnote "*Adoption
percentage based on global GBV in Q4 2025" (4Q25 letter, D022), and "roughly 20% of global GBV came from Reserve Now, Pay Later
bookings" (1Q26 letter, D031). The 2Q26 call's "over 20% of our total GBV" (D043) is a mirror. No letter, 10-Q, 10-K or the
proxy gives an RNPL share of nights, of bookings (count), or of listings-eligible nights; the "70% of people that we offer …
take us up" (3Q25 call, D005) is a take-up rate among offered guests, not a nights share, and is call-only. There is no
same-quarter GBV-share / nights-share pair, so the RNPL ADR premium cannot be pinned from filings.

## 6. Fetch log (www.sec.gov only; User-Agent reused verbatim from `analysis/src/pitch_model_v2/adr_engine/sizemix_adjudication.py` line 63)

| # | URL | UTC | HTTP | bytes | saved as |
|---|---|---|---|---|---|
| 1 | https://www.sec.gov/Archives/edgar/data/1559720/000155972025000030/abnb-20250930.htm (3Q25 10-Q, acc 0001559720-25-000030) | 2026-09-22T19:32:55Z | 200 | 1,478,397 | `C5_fetched_abnb_2025q3_10q.html` |
| 2 | https://www.sec.gov/Archives/edgar/data/1559720/000119312526175062/d936646ddef14a.htm (DEF 14A, acc 0001193125-26-175062, filed 2026-04-24) | 2026-09-22T19:32:56Z | 200 | 1,008,113 | `C5_fetched_abnb_2026_def14a.html` |

Both URLs were resolved from documents already on disk (A04 audit log for the 10-Q; the 2026-09-17 EDGAR submissions JSON for
the proxy), so no index page was fetched. Nothing touched airbnb.com. No file outside this folder was written.

## 7. Method

`py -3.13 C5_filing_search.py [--fetch]`: BeautifulSoup/lxml text extraction, regex sentence split, 15 term patterns (RNPL,
Reserve Now, Pay Later, Pay Less Upfront, flexible/deferred payment, payment program, cancellation, single/host-only fee,
simplified fee/pricing, fee structure, service fee, total price, guest fee), a hit is any sentence matching a term with a number
(%, bp, points, $, multiples, spelled-out numbers) anywhere in a ±2-sentence window; `classification` is rule-based and every
"check by hand" row was read (all are KPI tables, insurance revenue, or a fee-structure explanation on the 4Q25 call). The
transcripts are included only to verify the quotes and are flagged `filed=False` in both CSVs. Letters are parsed from the
Ex 99.1 HTML (image-heavy pages lose layout, which is why a few window strings read as jumbled infographic captions).

## 8. What the authors should change

1. Replace "Airbnb did not name RNPL in a filing at all until 2Q26" with: *"'Reserve Now, Pay Later' is named in every
   shareholder letter (8-K Ex 99.1) from 3Q25 on and in the FY25 10-K and the 2026 proxy; the 10-Q series first names it, as
   'RNPL', in 2Q26."*
2. Replace "both shareholder letters" / "exhaustive" with the ten-document list in §2; the label "transcript-only" for the
   *magnitude* is now supported by a search of every filed document that could plausibly carry it.
3. Say that the 0.8–1.2pp band is a judgement around GBV-minus-nights point readings, and that management's rounding alone
   permits roughly 0–2pp.
4. Note that the 1Q26 "~3 / ~4 points" includes ~6 weeks of the ex-NA RNPL leg, which the lap calendar assigns to 1Q27.

RESUME: nothing further to search on EDGAR for this question; the only unfetched related item is the DEFA14A (2026-04-24),
a proxy supplement that will not carry a product magnitude. If a future filing (3Q26 10-Q, ~5 Nov 2026) adds a number, re-run
`C5_filing_search.py` after adding the file to `DOCS`.
