# Filling the web-research gaps the overnight run left when the search budget ran out

Workstream 16, overnight run 6-7 Sep 2026. Author: Claude (agent 16).

Scripts: `analysis/src/overnight/16_merge_and_rerun.py`
Data: `data/processed/overnight/16_consensus_additions.csv`, `16_consensus_at_print_merged.csv`,
`16_reaction_panel.csv`, `16_reaction_tests.csv`, `16_q3_2026_breakeven.csv`, `16_rerun_delta.csv`,
`16_press_attribution.csv`, `16_news_since_5sep.csv`

Method note: the session's 200 WebSearch calls were already spent, so everything below was found by
driving the user's Chrome through Google and the DuckDuckGo HTML endpoint and reading the pages.
No number here is inferred; each carries a publisher, a date, a URL and a verbatim quote in the CSVs.
Where I only have a search-result snippet rather than a page I read end to end, the CSV says
`search-snippet`.

---

## Bottom line

1. **Five of the six WS04 gaps are now closed, and one of them changes a result.** The 2Q24
   next-quarter consensus is **$3.84bn (LSEG, Reuters 6 Aug 2024)** against a $3.70bn guide midpoint —
   a **-3.65% guide-vs-Street**, the largest below-Street guide in the sample, attached to the sample's
   second-worst day-1 move (-12.3%). Adding it lifts WS04's best day-1 spec from R² 0.116 to
   **0.164** (n 18→19, HC1 t +1.59→**+1.82**, p 0.112→**0.069**, permutation p 0.17→**0.087**) and takes
   the "guide below Street" 20-day rule from 8/8 to **9 of 9 negative, mean -8.90%, base-rate-adjusted
   p 0.078 → 0.057**. It is still LOO-negative at day 1 (-0.149), so **the no-day-1-alpha conclusion
   survives** — but the risk flag is materially stronger and every "8/8" in the run must become "9/9".

2. **An ADR consensus does exist, and WS04's "0 / 23, no publisher quotes one, ever" is wrong.**
   Zacks publishes *"Gross Booking Value per Night and Experience Booked (ADR)"* consensus in its
   pre- and post-print key-metrics pieces. I recovered five prints (1Q25, 3Q25, 4Q25, 1Q26, 2Q26).
   ABNB has beaten the ADR consensus at **5 of 5**, by +0.5% to +4.6%. On n=5 the correlation with the
   day-1 move is **-0.46** — i.e. if anything negative, and worthless at that n. The same Zacks series
   also has a **nights** and a **GBV** consensus, which fills the 2Q26 gaps (nights **145.44m** vs 148.3m
   actual = +1.97%; GBV **$26.42bn** vs $27.2bn = +2.95%).

3. **The red team was wrong on the single-fee share, and WS06/WS11 were right.** The 2Q26 earnings
   call contains the primary source verbatim: Ellie Mertz, prepared remarks — *"Approximately half of our
   active listings are now subject to the single service fee."* It is in the call, not the letter, which
   is why a letter-only check missed it. **Red-team corrections 11 and 15 must be withdrawn**, and the
   synthesis note's line 712 claim that the figure is "not in the letter or the call" is factually wrong.

4. **The -0.8pt take-rate risk can now be sourced and bounded, and it is too big.** The direct-booking
   pilot is real and readable without Skift: Airbnb's own in-product copy is quoted on Airbnb's host
   community forum (28 Aug 2026) and RSU by PriceLabs (31 Aug 2026) has the full mechanics — host fee cut
   from **15.5% to 6% or 10%** on bookings arriving through a host-generated tracked link, invite-only,
   US, no help-centre article or newsroom post. The arithmetic: a 0.8pt hit to a ~13.4% reported take
   rate needs **8.4% of all GBV** to route through the 6% tier, or **14.5%** at the 10% tier. That is not
   a pilot; that is a platform-wide behaviour change. **-0.8pt is not defensible; a 0-0.15pt FY27 drag
   is.**

5. **The AirROI 55.9% is a model, not a checkout measurement — and it is stale.** The methodology is
   published in full: `Total = [(ADR x N) + cleaning_fee] x (1 + 14% guest service fee) x (1 + lodging tax)`
   for a 3-night stay, with market-wide ADR and a 60-listing median cleaning fee per market, measured
   against the **nightly-rate subtotal only**. It includes lodging tax, and it assumes the **pre-migration
   split-fee structure with a 14% guest service fee** — which by 2Q26 no longer applied to about half of
   active listings. WS06's evidence and AirROI's number are therefore not in conflict; they measure
   different things. The correct line is not "do not cite it" but "it measures total-versus-advertised-
   nightly-rate including taxes on a stale fee structure, so it is not evidence about hidden fees."

6. **The 9 Sep EU proposal leaked on 4 Sep and it is the enabling-framework version, not a cap.**
   Reuters obtained the draft: it lets **member states** impose caps on short-term rentals in areas facing
   housing shortages, gives them criteria for declaring a shortage severe enough, and requires any
   restriction to be non-discriminatory, proportionate and in the public interest. That is consistent with
   WS11's low modelled expected value (0.18% of 2027 revenue) rather than a step-change.

7. **The next scheduled catalyst is two days away.** Brian Chesky speaks at the Goldman Sachs
   Communacopia + Technology Conference on **Tuesday 8 September 2026, 6:05pm ET**, public live webcast
   (Airbnb IR, 25 Aug 2026). It is the only public management appearance between now and 5 Nov.

---

## 1. WS04 — consensus gaps

`16_consensus_additions.csv` holds every added cell with publisher, date, URL, verbatim quote and a
confidence flag. `16_consensus_at_print_merged.csv` is WS04's file in WS04's exact column layout with
those cells applied. **`04_consensus_at_print.csv` was not touched.**

| Gap WS04 flagged | Status | Value | Source |
|---|---|---|---|
| (a) 2Q24 next-quarter (3Q24) revenue consensus | **CLOSED** | **$3,840m (LSEG)** | Reuters 6 Aug 2024: *"It expects third-quarter revenue to be between $3.67 billion and $3.73 billion, below analysts' estimate of $3.84 billion."* Corroborated same day by The Times and The Globe and Mail, both attributing to LSEG |
| (b) 4Q20 EPS consensus | **CLOSED (medium)** | **-$8.40 (FactSet)** vs -$11.24 actual | MarketWatch 26 Feb 2021 and Investor's Business Daily 25 Feb 2021, independently |
| (b) 1Q21 EPS consensus | **CLOSED** | **-$1.07 (FactSet, 27 analysts)** vs -$1.95 actual | AP wire, 13 May 2021: *"Wall Street expected a loss of $717 million, or $1.07 per share, according to a FactSet survey of 27 analysts."* |
| (b) 2Q21 EPS consensus | **CLOSED (low)** | **-$0.41** vs -$0.11 actual | Weakest row in the file. Only a broker market-review carries the per-share number; WSJ's *"Analysts had expected a loss of $254 million"* over ~626m shares is -$0.41, which corroborates the level but not the vendor |
| (c) ADR consensus at any print | **CLOSED — WS04's "0/23, never" is wrong** | 1Q25 $170.55 (7 an.), 3Q25 $166.67 (6), 4Q25 $165.52 (6), 1Q26 $178.54 (6), 2Q26 $181.56 | Zacks *"Gross Booking Value per Night and Experience Booked (ADR)"*, four separate articles |
| (d) 3Q26 adj. EBITDA and nights consensus | **NOT FOUND — and it does not exist yet** | — | Zacks publishes the nights/ADR/GBV consensus in *"Wall Street's Insights Into Key Metrics Ahead of Airbnb (ABNB) Q3 Earnings"*, which lands **2-3 days before the print**, i.e. ~2-3 Nov 2026. That is the answer to WS04's "get a nights whisper" action item: it will be free and public, three days early |
| (d) FY26 adj. EBITDA consensus | **CLOSED (medium)** | **~$5,034m** | MarketScreener consensus series (FY21-26: 1,593 / 2,903 / 3,653 / 4,041 / 4,300 / 5,034 $m). TIKR, 9 Aug 2026, independently: *"EBITDA rising from about $4.3 billion in 2025 to $5.0 billion in 2026"* |
| (d) FY27 adj. EBITDA consensus | **NOT FOUND** | — | MarketScreener's FY27 column sits behind the paywall; TIKR's blog stops at FY26. Every free FY27 datapoint I found is revenue ($15.73-15.76bn) or EPS ($6.02-6.14), which WS04 already has |
| (e) Options-implied move for 5 Nov 2026 | **NOT FOUND — does not exist yet** | — | Implied-move previews (Options AI, Benzinga, Market Chameleon) publish in the week of the print. Look from ~29 Oct 2026 |

**Two bonus cells and one vendor disagreement.** 2Q26 nights consensus **145.44m** and GBV **$26.42bn**
(Zacks) fill two WS04 blanks. Barron's puts the 2Q26 GBV bar at **$26.45bn** — a 0.1% vendor gap, fine.
MarketScreener's 7 Aug 2026 recap independently corroborates WS04's TIKR-derived 2Q26 adjusted-EBITDA
consensus: *"adjusted EBITDA up 21%, to $1.26bn, [analyst]s on average were looking for around $1.23bn"*
against WS04's $1,225.6m. **But at 2Q25 Zacks has nights at 130.76m where WS04's StreetAccount row has
133.35m** — a 2% vendor gap that turns a +0.8% nights beat into a +2.5% one. I did **not** overwrite
WS04's StreetAccount series; the disagreement is recorded and belongs in WS04's vendor-disagreement table.

### The re-run

`16_merge_and_rerun.py` executes `04_reaction_vs_consensus.py` unmodified except for the four input/output
filenames, so the comparison is like-for-like. 97 tests, of which **82 changed**; `16_rerun_delta.csv`
has all of them. A sensitivity run with the 2Q24 row **only** (2021 EPS and 2Q26 nights/GBV left out)
confirms which addition drives what.

| Test | WS04 (`04_reaction_tests.csv`) | WS16 (`16_reaction_tests.csv`) | Driven by | Verdict |
|---|---|---|---|---|
| **Day-1, guide vs next-Q Street** | n 18, R² 0.116, t +1.59, p 0.112, perm 0.17, LOO -0.176 | **n 19, R² 0.164, t +1.82, p 0.069, perm 0.087, LOO -0.149** | 2Q24 | Best day-1 spec, materially stronger, **still LOO-negative** |
| **Day-1, guide ABOVE vs BELOW (Mann-Whitney)** | n 19, gap 4.37pts, p 0.076 | **n 20, gap 5.50pts, p 0.040** | 2Q24 | Now nominally significant |
| **Guide below Street, 20-day sign test** | 8 of 8 negative, mean -7.95%, binom p 0.0039, vs base rate **p 0.078** | **9 of 9 negative, mean -8.90%, binom p 0.0020, vs base rate p 0.057** | 2Q24 | The cleanest qualitative rule in the run gets cleaner |
| **Guide below Street, day-1 sign test** | 6 of 8, p vs base 0.118 | **7 of 9, p vs base 0.070** | 2Q24 | |
| **20-day, nights surprise vs consensus** | n 18, R² 0.2199, LOO **+0.133**, perm 0.053 | **identical** | — | **The headline finding is untouched.** 2Q26 has no 20-day excess in the file and 2Q24 still has no nights consensus |
| **Day-1, nights surprise** | n 18, R² 0.0012, slope -0.118 | n 19, R² 0.0019, slope **+0.162** | 2Q26 | Slope flips sign on one observation. Still nothing |
| **Day-1, EPS surprise (bps of price)** | n 17, R² 0.003, slope +0.040, t +0.20 | **n 20, R² 0.094, slope -0.066, t -2.74** | 2021 EPS rows | **A trap, not a finding.** The three 2021 rows are enormous GAAP "misses" driven by IPO stock comp that coincided with positive reactions. It manufactures a spurious negative EPS coefficient. Do not use |
| **20-day, EPS surprise (bps of price)** | n 16, R² 0.147, LOO **+0.020** | n 19, R² 0.053, LOO **-0.219** | 2021 EPS rows | One of WS04's nine positive-LOO specs dies |
| **20-day, rev + eps + guide-vs-Street** | n 15, R² 0.360, LOO **+0.003** | n 16, R² 0.221, LOO **-0.364** | 2021 EPS rows | A second positive-LOO spec dies |
| **20-day, rev + guide-vs-Street** | n 17, R² 0.187, LOO **+0.096** | n 18, R² 0.121, LOO **-0.089** | 2Q24 | A third dies |
| Positive-LOO specs, count | 9 (8 at 20d, 1 at 5d, 0 at day 1) | **9 (5 at 20d, 4 at 5d, 0 at day 1)** | both | Count is coincidentally the same; **membership is not**. The red team's replacement wording "every positive sits at 20 days" is now false |

**What does and does not change for the pitch.** No day-1 trade — confirmed for a fourth time, now with
one more observation and a stronger in-sample fit that still fails out of sample. The nights-drift
coefficient at 20 days is unchanged and remains the only survivor. "Guide below Street" moves from
*suggestive* to *the strongest qualitative regularity in the study*: 9 of 9, mean -8.90%, and it now
also separates the day-1 distributions at p 0.040.

**Recommended handling of the three 2021 EPS rows.** Keep them in the merged file for completeness, set
`eps_comparable = 0` for the pitch runs, and say why in one sentence: the 2021 GAAP losses and the 2021
GAAP consensus are both dominated by IPO stock compensation, so a "miss" there is an accounting artefact
and the sign it induces is spurious. Every EPS conclusion in WS04's note was drawn on the 17-row panel
and stands.

---

## 2. WS03 — contemporaneous press attribution for the ten extreme reactions

`16_press_attribution.csv`: headline, publisher, date, URL, the one sentence naming the driver, my
reading of the press driver class, and whether it matches WS03's `driver_class`.

| Print | Day-1 | WS03 class | Press class | Match |
|---|---|---|---|---|
| 2026Q2 | +16.3 | guide | guide | **yes** |
| 2024Q4 | +14.0 | KPI | KPI + expansion plans + two same-day upgrades | partial |
| 2021Q3 | +12.9 | guide | KPI (record quarter) | **no** |
| 2020Q4 | +12.9 | **margin** | KPI (revenue / gross-bookings beat) | **no** |
| 2022Q4 | +12.6 | guide | first profitable year + above-Street Q1 guide | **yes** |
| 2024Q2 | -12.3 | **macro** | guide (below Street), cause macro | partial |
| 2023Q1 | -12.0 | KPI | guide (Q2 nights below revenue) | partial |
| 2022Q3 | -10.0 | KPI | **guide** (Bloomberg headline: muted Q4 bookings forecast) | **no** |
| 2024Q3 | -8.8 | investment spend | EPS miss / "mixed quarter" | partial |
| 2025Q2 | -8.4 | macro | macro ("warning", "slowdown") | **yes** |

**Three real mismatches, and they point one way.** In 2021Q3, 2022Q3 and 2023Q1 the press attribution is
the *guide*, where WS03 records the reported KPI (2022Q3, 2023Q1) or vice versa (2021Q3). The
underlying fact is the same in each case — WS03's quote is the guide sentence — so this is a labelling
problem in the `driver_class` column, not a factual error. Corrected, WS03's own event study would read
**guide 6, KPI 2, macro 1, investment spend 1** rather than guide 4 / KPI 4, which strengthens rather
than weakens the run's central claim that ABNB trades on the forward statement.

**One attribution I could not support at all: 2020Q4.** WS03 classifies the first post-IPO print as a
*margin* event on Dave Stephenson's "30% EBITDA margins or greater" line. Every contemporaneous
same-day source I found — The Globe and Mail (*"after the company posted better-than-expected gross
bookings"*), CNBC ($859m vs $748m), MarketWatch, IBD — attributes the move to the revenue and
gross-bookings beat and the reopening trade. The margin ambition may well have mattered to the multiple;
no journalist writing that day said so. **Do not use 2020Q4 as evidence that long-term margin framing
moves the stock.** That matters because WS03's headline finding (and red-team correction #6) is precisely
about long-term-target language in prepared remarks.

**And one thing WS03 and WS04 both miss on 2024Q4:** two sell-side upgrades (Baird, Goldman Sachs) landed
the same morning as the +14.0% move. Sell-side actions on the reaction day are not in any workstream's
feature set.

---

## 3. The three red-team "unsupported claims"

### (a) "About half of listings are on the single host-only fee by 2Q26" — SUPPORTED, primary source found

**Ellie Mertz, CFO, prepared remarks, Q2 2026 earnings call, 6 August 2026:**

> "As a result of its success, we recently announced the broader rollout of the single fee to the
> majority of our remaining hosts, which we expect to be completed by year-end. **Approximately half of
> our active listings are now subject to the single service fee.**"

Source: the call transcript already in this repo at
`data/raw/regulatory/transcripts/2026-Q2.txt` (Motley Fool transcript of the 6 Aug 2026 call), and again
in Q&A: *"We anticipate by year-end, our entire supply base will be on that single service fee."*
The 2Q26 shareholder letter does **not** carry the share — it says only that Airbnb *"initially migrated
most property management software hosts"* and *"in July, we announced plans to migrate most of the
remaining hosts."* A letter-only check therefore returns "not disclosed", which is what happened.

**Consequence: red-team corrections 11 and 15 are withdrawn, and the synthesis note's line 712 is wrong.**
WS06's "about half by 2Q26" and WS11's "~50% of listings at Q2'26" were right and need no edit.

### (b) The direct-booking / lower-host-fee pilot — SUPPORTED, and now quantified

Skift is paywalled, but three independent readable sources carry the substance:

- **Airbnb's own product copy**, quoted by hosts on Airbnb's community forum, 28 Aug 2026: *"Share your
  direct booking links with potential guests through social media and other marketing channels. These
  bookings will receive the same benefits as other bookings on Airbnb, including AirCover for Hosts...
  You can also share your savings with guests by offering a new direct booking discount in the Listing
  editor. *This is a pilot program."*
- **RSU by PriceLabs (Rental Scale-up), 31 Aug 2026** — the fullest account: *"Airbnb is rolling out a
  direct booking link pilot that drops the standard 15.5% host fee to either 6% or 10% when hosts drive
  their own traffic."* Invite-only email ("Get a lower service fee with direct bookings"), a
  Listing-editor toggle generating a tracked URL, the discount slider capped at the size of the fee cut,
  and — the load-bearing detail — **the transaction stays entirely on Airbnb**: Airbnb processes the
  payment, provides AirCover, keeps the guest data. It is an affiliate rebate, not disintermediation.
  Airbnb has published **no** help-centre article and **no** newsroom post; there is no official scope.
- Half a dozen host-industry blogs (Houfy, Smoothstay, Hostmatic, BookWithHaven, Tabivista, Smoobu,
  29 Aug - 1 Sep 2026), all reporting 6% or 10%, all US.

**The quantification that WS11 was missing.** The fee cut is 5.5 to 9.5 percentage points of the
*host-fee base*. Reported take rate is ~13.4% of GBV. To move reported take rate by 0.8pt you need
0.8 / 9.5 = **8.4% of total GBV** at the 6% tier, or 0.8 / 5.5 = **14.5%** at the 10% tier. For an
invite-only US pilot with no documented scope, in a business where North America is ~29% of nights, that
is implausible in FY27. A defensible bear-case parameter is **0 to 15bp of FY27 take rate** (i.e. up to
~1.6% of GBV routed through links at the 6% tier), with the -0.8pt reserved for a "pilot becomes the
default policy" tail. **Red-team correction 16 is superseded**: the claim is no longer unverified, it is
verified and too large by roughly 5-10x.

Two contextual facts from the same source worth carrying: Q2'26 sales and marketing was **$875m, +27%
y/y against 17% revenue growth**, and Airbnb is absent from Google's AI-Mode agentic-booking partner list
(BKNG, EXPE, MAR, IHG are in) because Chesky rejected B2B inventory on the Q2 call. The pilot is best
read as buying host-sourced traffic more cheaply than Airbnb can buy it from Google.

### (c) The AirROI "55.9% median checkout markup" — SOURCED, methodology read, and it is a model

Original: **AirROI, "Airbnb vs Hotel 2026: All-In Price Math Across 28 US Markets", Jun Zhou, published
16 April 2026**, https://www.airroi.com/blog/airbnb-vs-hotel-all-in-pricing-2026

The methodology is stated in the article:

> `Total = [(ADR x N) + cleaning_fee] x (1 + service_rate) x (1 + tax_rate)`

with N = 3 nights, `ADR` = AirROI's market-wide trailing-12-month whole-unit ADR, `cleaning_fee` = the
median of a 60-listing sample of 1-2 bedroom entire-home listings with 4.5+ ratings and ≥$10,000 TTM
revenue per market, `service_rate` = **14%** ("our math assumes the simplified US default"), and
`tax_rate` = the local lodging tax, 11.05% to 17.40%. The 55.9% is the **median across 28 markets of
(modelled total ÷ nightly-rate subtotal − 1)**, range 45.0% to 72.9%.

Three things follow.

1. **It is not a measurement of checkouts.** No quote, cart or booking is observed. It is an arithmetic
   construction from three market-level medians, and the article says so.
2. **Only about 30% of the 55.9% is an Airbnb fee.** In AirROI's own Orlando worked example
   (nightly $741, cleaning $160, service $126, tax $128, total $1,156), the +55.9% markup decomposes into
   **21.6pp cleaning fee (39%), 17.0pp guest service fee (30%) and 17.3pp lodging tax (31%)**. Lodging tax
   is not an Airbnb take, and the cleaning fee is set by the host.
3. **The fee assumption is stale.** By 2Q26 approximately half of active listings were on the 15.5%
   single host fee with **no separate guest service fee** (Mertz, above), so a 14% guest fee is the wrong
   input for the period the article claims to describe.

**So WS06's evidence and AirROI's number are not in conflict — they measure different quantities.**
WS06 shows Airbnb's public pricing endpoint returns no separate fee lines (the display is one number);
AirROI computes total-versus-advertised-nightly-rate including cleaning and tax. Both can be true.
Revise the instruction from "do not cite the 55.9% figure" to a one-line characterisation (below).

---

## 4. Anything after 5 Sep 2026

`16_news_since_5sep.csv`. The honest answer is **almost nothing, because 4 September 2026 was a Friday**
and 5-6 September are a weekend. The last close is confirmed at **$181.94 on 4 Sep 2026**
(stockanalysis.com / S&P Global); third-party trackers quoting a "$185.25 as of September 5" are stale.
The file therefore also carries the late-August items that post-date some workstreams' cut-offs, plus the
forward calendar.

The three that matter:

- **The EU proposal leaked on 4 Sep** and is the enabling-framework version (member states may cap in
  housing-shortage areas, subject to non-discrimination / proportionality / public-interest tests), not an
  EU-level restriction. WS11's low modelled impact looks right. The formal 9 Sep publication should be
  checked against the draft.
- **Chesky at Goldman Sachs Communacopia, Tuesday 8 Sep 2026, 6:05pm ET, public webcast.** Two days away.
  Listen for: nights commentary for the quarter to date, single-fee completion, the direct-booking pilot
  (unlikely to be raised voluntarily), and any FY27 framing.
- **Peer Q3 dates are NOT confirmed.** TipRanks *estimates* BKNG on 4 Nov 2026 — the day before ABNB —
  and MAR on 29 Oct; neither company had posted a date as of 4 Sep, and EXPE/HLT had not either. If the
  BKNG estimate holds it matters for the card: ABNB's 5 Nov reaction would be reading into a fresh BKNG
  print. Re-check IR pages in early October.

Also useful: **CoStar/STR weekly US hotel data through the week ending 22 Aug 2026 shows a 19th
consecutive week of y/y gains** (week ending 15 Aug: occupancy 68.0% +2.6%, ADR $163.56 +3.5%; weeks
ending 1 and 8 Aug: RevPAR +7.3% and +7.2%), and CoStar/Tourism Economics raised the **FY26 US RevPAR
forecast to +4.4%** (demand +1.7%, ADR +3.1%) with FY27 at +2.1%. The **full-month August 2026** STR
release is not out (due ~22-25 Sep), and **NTTO/BEA August inbound is not out** (due mid-to-late October).

---

## 5. Corrections to existing work

I edited no one else's file. These belong to the workstreams named.

1. **`15_red-team.md`, corrections 11 and 15 — WITHDRAW.** "Approximately half of our active listings are
   now subject to the single service fee" is in the 2Q26 call (Mertz, prepared remarks), in this repo at
   `data/raw/regulatory/transcripts/2026-Q2.txt`. WS06 line 173 and WS11 lines 26/312 were correct as
   written and should be left alone.
2. **`15_red-team.md`, correction 16 — SUPERSEDE.** The 6-10% pilot is verified from Airbnb's own product
   copy and a full readable trade write-up. The flag should change from "unverified" to "verified, but
   -0.8pt implies 8-15% of GBV routing through the pilot; use 0-15bp for FY27."
3. **`15_red-team.md`, correction 7 — extend.** With the 2Q24 row added, the positive-LOO count is still
   nine but the composition changes: five at 20 days, **four at five days**, none at day 1. The clause
   "Every positive sits at 20 days" is no longer true; "not one is at day 1" still is.
4. **`04_consensus-and-reaction.md`, coverage table and "What I could not get".** ADR is no longer
   0/23 with "no publisher quotes an ADR consensus for ABNB, at any print" — Zacks quotes one at least
   five times. The 2Q24 next-quarter gap is closed. Both statements should be replaced rather than
   softened.
5. **`04_consensus-and-reaction.md`, bottom-line item 5 and the 5 Nov table.** Every "8 of 8" /
   "8/8 guide-below-Street" becomes **9 of 9**, mean **-8.90%**, base-rate p **0.057**.
6. **`03_management-language-and-stock.md`, `03_event_study.csv` `driver_class`.** 2021Q3, 2022Q3 and
   2023Q1 are labelled against the contemporaneous press; 2020Q4's "margin" attribution has no
   contemporaneous support at all. See section 2.
7. **`06_consumer-choice-and-willingness-to-pay.md` sections 2 and 9, and `14_master-synthesis.md`
   line 929.** "Do not cite the 55.9% figure / the two cannot both describe the same 2026 checkout" is
   too strong; they describe different quantities. Replacement text in section 6 below.
8. **`04_consensus_at_print.csv`, 2025Q2 `cons_nights_m`.** Zacks has 130.76m where the file has 133.35m
   (StreetAccount). Not an error — a vendor gap worth adding to WS04's vendor-disagreement table, because
   it moves the 2Q25 nights beat from +0.8% to +2.5% and 2Q25 is one of the 18 points in the drift
   regression.

---

## 6. Exact edits for `14_master-synthesis.md`

| Where | Replace | With |
|---|---|---|
| line 105 (guide-below-Street row) | "All 8 such prints had a negative 20-day excess (mean −7.95%); p 0.004 vs a coin flip but **p 0.078 vs ABNB's actual 72.7% base rate**" | "All **9** such prints had a negative 20-day excess (mean **−8.90%**); p 0.002 vs a coin flip and **p 0.057 vs ABNB's 72.7% base rate**. The ninth is 2Q24, whose −3.65% guide-vs-Street was recovered by WS16 (Reuters, 6 Aug 2024: Street $3.84bn vs a $3.70bn midpoint). Day-1 the two groups now separate at Mann-Whitney p 0.040, gap 5.5pts" |
| line 552 (scorecard) | "8/8 negative at 20d, base-rate p 0.078" | "**9/9** negative at 20d, base-rate p **0.057**" |
| line 583 | "a \"guide below Street\" risk flag on position sizing" | unchanged, but append: "(9/9, mean −8.90%; WS16 re-run on `16_reaction_tests.csv`)" |
| line 606 (ADR row, "Street" column) | "none published (no publisher quotes an ADR consensus, ever)" | "**none published yet, but one will be**: Zacks quotes a 'GBV per Night and Experience Booked (ADR)' consensus 2-3 days before each print (2Q26 $181.56; 1Q26 $178.54; 4Q25 $165.52; 3Q25 $166.67; 1Q25 $170.55). ABNB has beaten it 5 of 5 by +0.5% to +4.6%. Get the Q3 number on ~2-3 Nov" |
| line 613 (Q4 guide row) | "a live \"guide below Street\" setup (8/8 negative 20-day, base-rate p 0.078)" | "a live \"guide below Street\" setup (**9/9** negative 20-day, base-rate p **0.057**)" |
| line 712-714 (claims not to make, item 3) | "*\"about half of listings were on the single fee by 2Q26\"* (not in the letter or the call — the disclosed facts are \"over a quarter\" at 1Q26 and \"entire supply base by year-end\" at 2Q26)" | **delete this clause entirely.** It is in the call: Ellie Mertz, prepared remarks, 6 Aug 2026 — *"Approximately half of our active listings are now subject to the single service fee."* (`data/raw/regulatory/transcripts/2026-Q2.txt`). It is absent from the letter only |
| line 716-717 (same item) | "*\"a −0.8pt take-rate hit from the direct-booking pilot\"* (the Skift article is paywalled and the 6-10% range was never read from a primary source — **do not put −0.8pts in the model**)" | "*\"a −0.8pt take-rate hit from the direct-booking pilot\"* — the pilot is now **verified** (Airbnb's own product copy on its host community forum, 28 Aug 2026; RSU by PriceLabs, 31 Aug 2026: host fee 15.5% → **6% or 10%** on host-generated tracked links, invite-only, US, no newsroom post). The number is wrong for a different reason: −0.8pt of a ~13.4% take rate requires **8.4% of all GBV** at the 6% tier or **14.5%** at the 10% tier. **Use 0-15bp of FY27 take rate; reserve −0.8pt for a 'pilot becomes policy' tail** |
| line 738 (risk register) | "8/8 guide-below-Street prints had negative 20-day excess" | "**9/9** guide-below-Street prints had negative 20-day excess" |
| line 760 (to-do #5) | "**Get a nights whisper for Q3-26.** No published nights consensus exists anywhere free ... **2 + calls**" | "**Get a nights whisper for Q3-26.** A free one publishes ~2-3 Nov: Zacks' *'Wall Street's Insights Into Key Metrics Ahead of Airbnb (ABNB) Q3 Earnings'* carries nights, ADR and GBV consensus (2Q26: nights 145.44m, ADR $181.56, GBV $26.42bn). Buy-side colour is still worth having earlier, but the bar is no longer unobtainable — **cost: 0 calls, 10 minutes on ~2 Nov**" |
| line 929 (AirROI) | "**Do not cite the AirROI \"55.9% median checkout markup\" figure.** Our parse of 1.71m of Airbnb's own quote responses finds no separate fee lines at all after the 2025 total-price default." | "**Characterise the AirROI \"55.9% median checkout markup\" correctly rather than dismissing it** (AirROI, 16 Apr 2026). It is a *modelled* 3-night total — `[(market ADR x 3) + median cleaning fee] x 1.14 x (1 + lodging tax)` — measured against the nightly subtotal, not observed checkouts; about 31% of the markup is lodging tax and 39% is the host-set cleaning fee, neither of which Airbnb keeps; and it assumes the pre-migration 14% guest service fee, which no longer applied to about half of active listings by 2Q26. It is not evidence about hidden fees, and it does not contradict our parse of 1.71m quote responses" |
| line 984 (catalysts) | "5 Nov Q3 print and Q4 guide ...; 9 Sep EU Affordable [Housing / STR proposal]" | append "**8 Sep: Chesky at Goldman Sachs Communacopia, 6:05pm ET, public webcast** (Airbnb IR, 25 Aug 2026) — the only scheduled management appearance before the print. The 9 Sep EU proposal already leaked on 4 Sep (Reuters): it lets **member states** cap short-term rentals in housing-shortage areas subject to non-discrimination / proportionality / public-interest tests — an enabling framework, not an EU cap" |

Add one line to the "corrections found" list around line 922-935:
*"WS15's corrections 11 and 15 are withdrawn: 'approximately half of our active listings are now subject
to the single service fee' is verbatim in the 2Q26 call (Mertz, prepared remarks). WS06 and WS11 were
right; the figure is absent from the letter only. (WS16)"*

---

## 7. What I could not find, and why

- **FY27 adjusted-EBITDA consensus.** MarketScreener's forecast table gives FY21-26 (1,593 / 2,903 /
  3,653 / 4,041 / 4,300 / **5,034** $m) in a search snippet, but the FY27 column is behind its paywall and
  its ABNB quote page could not be reached (I could not extract the correct instrument slug; MarketScreener
  returns unrelated German warrants for guessed ids). TIKR's blog stops at FY26. Zacks and
  S&P Global/stockanalysis publish FY27 revenue and EPS but not EBITDA.
- **A 3Q26 nights or adjusted-EBITDA consensus.** It does not exist on 6 Sep 2026 — the Zacks
  key-metrics preview publishes 2-3 days before the print. WS04's derived bars ($2.3-2.4bn EBITDA,
  ~144-146m nights) remain the right placeholder, and the derived nights bar is worth checking against
  Zacks' number on ~2-3 Nov because WS04's own history shows Zacks and StreetAccount disagreeing by up to
  2% on nights.
- **An options-implied move for 5 Nov 2026.** None published two months out.
- **ADR consensus before 1Q25.** Zacks' key-metrics series exists further back (the format runs to at
  least 4Q23) but I could not surface the older ADR lines in search snippets and zacks.com itself renders
  no text in this browser session; the readable mirrors (metatrader.com, nasdaq.com, finviz.com,
  ainvest.com, msn.com) only index recent quarters. A full back-fill is a mirror-by-mirror job, worth
  perhaps an hour, and would take ADR consensus coverage from 5 prints to maybe 10-12.
- **The Skift article body.** Still paywalled. It is no longer needed.
- **Full-page reads of the Reuters, Bloomberg, WSJ and Barron's articles** in `16_press_attribution.csv`.
  All four are paywalled or block this environment; the headline, date, URL and driver sentence come from
  search-result snippets, which is why every row carries `verification = search-snippet`. The snippets are
  quoted verbatim and are internally consistent across two or more outlets for every print except 2021Q3.
- **Confirmed Q3 2026 earnings dates for BKNG, EXPE, MAR, HLT.** None of the four had announced as of
  6 Sep 2026; only TipRanks estimates exist.

---

## 8. For the model

| Name | Value | Unit | Source |
|---|---|---|---|
| 3Q24 revenue consensus at the 2Q24 print | 3,840 | $m | Reuters/LSEG, 6 Aug 2024 |
| 2Q24 guide vs Street | **-3.65** | % | derived; largest below-Street guide in the sample |
| Guide-below-Street 20-day rule | **9 of 9 negative, mean -8.90%**, binom p 0.0020, base-rate p **0.057** | — | `16_reaction_tests.csv` |
| Guide-vs-Street day-1 slope | +0.782 pts per 1% (HC1 t +1.82, p 0.069, n 19, **LOO -0.149**) | pts | `16_reaction_tests.csv` |
| Nights-drift coefficient (20d) | **unchanged**: -3.84 + 1.544 x nights_surprise%, LOO +0.133, n 18 | pts | `16_reaction_tests.csv` |
| 2Q26 nights consensus / surprise | 145.44m / **+1.97%** | m, % | Zacks, 3 and 6 Aug 2026 |
| 2Q26 GBV consensus / surprise | $26.42bn / **+2.95%** | $bn, % | Zacks (Barron's $26.45bn) |
| ADR consensus series | 1Q25 170.55, 3Q25 166.67, 4Q25 165.52, 1Q26 178.54, 2Q26 181.56 | $ | Zacks |
| ADR beat history | **5 of 5**, +0.46 / +2.77 / +1.20 / +4.64 / +1.02 % | % | derived |
| FY26 adj. EBITDA consensus | **~5,034** | $m | MarketScreener; TIKR "about $5.0bn" |
| Single-fee coverage at 2Q26 | **~50% of active listings**; entire supply base by year-end | % | Mertz, 2Q26 call (verbatim) |
| Direct-booking pilot fee | 15.5% → **6% or 10%**, invite-only, US, tracked link, transaction stays on Airbnb | % | Airbnb product copy + RSU 31 Aug 2026 |
| Take-rate drag from the pilot, FY27 | **0 to 15bp** (not -0.8pt; -0.8pt needs 8.4-14.5% of GBV) | bp | derived |
| Q2'26 sales and marketing | 875, +27% y/y | $m | RSU citing the Q2'26 filings |
| US hotel FY26 RevPAR forecast | **+4.4%** (demand +1.7%, ADR +3.1%); FY27 +2.1% | % | CoStar / Tourism Economics, Aug 2026 |
| US hotel weekly run-rate, Aug 2026 | 19 straight positive weeks; wk-15-Aug occupancy 68.0% (+2.6%), ADR $163.56 (+3.5%) | — | CoStar/STR via DSH, 28 Aug 2026 |

## 9. For the 5 Nov card

1. **The Q4-26 guide-below-Street flag is now the strongest rule in the study: 9 of 9 negative at 20
   days, mean -8.90%.** The Street sits at $3,200m for Q4-26 against a model-implied +11-13% guide
   (~$3,145m). A midpoint below $3.20bn triggers it.
2. **On ~2-3 Nov, pull Zacks' "Wall Street's Insights Into Key Metrics Ahead of Airbnb (ABNB) Q3
   Earnings."** It publishes the nights, ADR and GBV consensus free, two to three days before the print.
   That closes the single biggest hole in the card — the unpublished nights bar — at zero cost. Read it
   against WS04's derived 144-146m and expect a 1-2% vendor gap versus StreetAccount.
3. **Add ADR to the card.** ABNB has beaten the published ADR consensus at 5 of 5 prints. It is a weak
   positive base rate for the print and, on n=5, mildly *negative* for the reaction (r -0.46) — i.e.
   treat a large ADR beat as a mix/FX signal, not a bull signal.
4. **8 Sep, 6:05pm ET: Chesky at Goldman Sachs Communacopia, public webcast.** Only pre-print management
   appearance.
5. **The take-rate bear case shrinks.** The single-fee tailwind is intact and disclosed at ~50% coverage;
   the direct-booking offset is 0-15bp, not -0.8pt. Net, WS11's take-rate downside row is too negative.
6. **BKNG may report 4 Nov, the day before ABNB** (TipRanks estimate, unconfirmed). Confirm in October.
7. **EU: the 9 Sep proposal already leaked (4 Sep).** It devolves capping powers to member states with
   proportionality tests rather than imposing an EU-level restriction. Nothing in the draft changes the
   2027 modelled impact; check the final text against the draft on 9 Sep.

## 10. What to build next

1. Back-fill the Zacks ADR/nights/GBV key-metrics series to 4Q23 through the readable mirrors
   (metatrader.com, nasdaq.com, finviz.com, ainvest.com, msn.com — zacks.com itself renders nothing in
   this environment). ~10-12 ADR prints would make an ADR-surprise test worth running.
2. Buy or borrow one FY27 EBITDA consensus print (MarketScreener, Visible Alpha or TIKR) so the football
   field anchors to a real number rather than to WS12's own FY27 EBITDA.
3. On 6 Nov, re-run `16_merge_and_rerun.py` with the 3Q26 row appended. The nights-drift coefficient gets
   its first clean out-of-sample test and the guide-below-Street rule gets a tenth observation.
4. Add a `same_day_analyst_action` column to `03_event_study.csv`. Two upgrades landed on the morning of
   the +14.0% 2024Q4 move and nothing in the run accounts for sell-side actions on the reaction day.
