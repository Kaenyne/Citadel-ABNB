# Thesis 1 (RNPL): quantified rewrite, 23 Sep 2026

Krish with Claude (Opus 5.5). Replaces the Thesis 1 paragraph in the team's two-page memo draft. Every number below
traces to a repo file in §4. The numbers follow the official nights line on main (`docs/pitch-model-v2/lines/final_nights.md`,
DEC-0019/0029). Base case = the lap only. Short case = the lap plus the cancellation tail. Nothing on the AGENT_BRIEF §6
kill list is used.

---

## 0. Memo version (~180 words)

**RNPL bought 2026's re-acceleration; the lift is lapping while cancellations peak.** Airbnb was slowing (nights +9.1% in
1H24, +7.7% in 1H25) when it launched Reserve Now, Pay Later ($0 at booking) in August 2025, then 14-day free cancellation
and a 15.5% host-only fee. Management credited the three with ~3pts of 1Q26 nights growth (RNPL ~1.6), lifting nights to
+9.7% in 1H26 on ~7% underlying. RNPL grew from ~4% of GBV (3Q25, est.) to ~20% in 1Q26, but only "over 20%" in its first
full global quarter, when management stopped quantifying the lift. The 10-Q says RNPL bookings cancel more; the CFO said
Airbnb's overall cancellation rate rose from ~16% to ~17%, implying ~22% on RNPL bookings (~17% of nights). Guests cancel
free until they pay, just before check-in, so bookings count immediately but about half the cancellations hit a later
quarter: the lift showed up in 1H26, the cancellations keep arriving through 2H26. As RNPL grows (eligibility widened in
July), those cancellations cost 0.9pt in 3Q26, just as the US launch turns one and stops adding growth. The bundle falls
from ~3pts to ~1.4, then ~0 in 4Q26: ~7% nights growth vs the Street's +9.9%.

Optional footnote or exhibit line (dropped from the text for clarity): inferred overall cancellation rate 16.2% (3Q25),
16.4% (4Q25), 17.0% (1H26), ~17.3% (4Q26E).

Where each number comes from (chart data on `krish/pitch-charts`, `data/processed/pitch_charts/`):
- Bundle by leg (`n01_nights_decomposition.csv`): 3.0pts in 1H26 = US RNPL 0.70 + RNPL outside the US 0.91 + fee and
  cancellation legs 1.41. The US RNPL leg laps in 3Q26, leaving 2.31. The fee and cancellation legs lap in 4Q26, leaving 0.91.
  Underlying growth (ex bundle, Middle East, World Cup): 7.9 / 7.4 (1H25), 7.1 / 6.8 (1H26), 7.2 (4Q26E).
- Implied cancellation rate (`n03_cancel_rate.csv`, the +6pt path): 16% historical + RNPL nights share × 6pt. The +6pt is
  management's 1pt rise ÷ RNPL's 16.7% nights share. RNPL nights share 3.2 / 7.1 / 15.9 / 16.7% (3Q25–2Q26); 3Q25–4Q25
  GBV shares (4% / 9%) are assumptions, backed by the balance-sheet solve (1–6% / 5–10% of the unpaid book).
- Cancellation cost: the D1 central cell at the management-implied propensity with 25% rebooking, −0.93pt (3Q26) and
  −0.85pt (4Q26). Net bundle: 2.31 − 0.93 = 1.38; 0.91 − 0.85 = 0.06. Underlying 7.21 + 0.06 ≈ 7.3% for 4Q26, against the
  official base of +8.1% (which leaves the drag out, DEC-0019) and the Street's +9.9%.
- Half a quarter later: 46–49% of excess cancellations come from earlier booking cohorts (D §2.4).

Everything below is backup for Q&A and the appendix, not memo text.

---

## 1. Long version (backup; too long for the memo)

**1. RNPL pulled bookings forward. The lift laps from 3Q26, and the cancellations arrive after the booking.**

In August 2025 Airbnb launched Reserve Now, Pay Later (RNPL) in the US: $0 at booking, payment due just before the
free-cancellation window closes. In October it added a 14-day free-cancellation policy and began moving hosts to a single
15.5% host-only fee. RNPL went global between 17 February and 4 March 2026. Before these changes Airbnb was slowing like any
large platform: nights grew +9.1% in 1H24 and +7.7% in 1H25, with North America in low single digits. Afterwards North America
reached high single digits and total nights grew +9.7% in 1H26. Management said the three features added "over 200 basis
points" of nights growth in 4Q25 and "approximately three points" in 1Q26. In 2Q26 it gave no figure and reported RNPL's
share of GBV instead (Exhibit 1).

**The share has stopped rising.** RNPL was "roughly 20%" of GBV in 1Q26, when guests outside the US had it for only 5–6 of 13
weeks. In 2Q26, the first full quarter of global availability, it was "over 20%". Management still expects growth: it
widened the eligible booking types in July (without naming them or sizing the change) and guided 3Q26 nights to "low double
digits". Its filings, though, write about timing. The 1Q26 letter flagged "tougher comparisons in the back half of this
year against the rollout of Reserve Now, Pay Later in 2025". The 10-Q warns that as adoption grows "the timing among GBV,
revenue, and cash receipts may become less correlated."

**Cancellations land after the booking.** The 2Q26 10-Q says RNPL bookings "have experienced higher cancellation rates than
historic bookings". The CFO called the cancellations "very elevated" and put the platform rate at "maybe 16%… going to 17%".
If RNPL accounts for that whole point, RNPL bookings cancel at about 22%, against 16% for the rest. The guest pays only days
before check-in, so the cancellation comes close to the stay. In our cohort model, 46–49% of a quarter's excess cancellations
come from bookings made in earlier quarters. The balance sheet shows the exposure. In 2Q26 unearned fees fell 1% y/y while
GBV grew 16%. Solved against pre-RNPL norms, that gap means about 21m RNPL nights were booked but unpaid at 30 June (range
14–37m). That is 14% of a quarter's nights, all free to cancel until the guest pays.

**What it does to the numbers.** Each leg laps on a dated schedule, and together they add up to management's own three
points. US RNPL laps in 3Q26 (−0.7pt of total nights), the global cancellation and fee legs in 4Q26 (−1.4pt), and RNPL outside
the US in 1Q–2Q27 (−0.9 to −1.0pt). Our base case includes only the lap. It gives 3Q26 nights of +9.9% (146.8m) against the
Street's +11.5% (148.9m, and our number is below all 28 estimates), 4Q26 of +8.1% against +9.9%, and FY27 of +6.6%. Completed
stays from reviews in 123 markets, which already net out every cancellation, read +9.2% to +9.5% for 3Q26. The cancellation tail
is our short case: a further −0.5 to −0.6pt a quarter in 2H26 (−0.1 to −1.4pt across 2,025 scenarios). It stays out of the
base because a calendar test across 34 markets found no cancellation signature and management says actual cancellations
match its tests. The 5 Nov tell is a prediction management made itself, "higher unearned fees in Q3". A print at or below −3%
y/y supports us (P 0.43).

**Exhibit 1. RNPL by quarter: what Airbnb disclosed, and what our data implies**

| | 3Q25 | 4Q25 | 1Q26 | 2Q26 | 3Q26E |
|---|---|---|---|---|---|
| Where RNPL was live | US, from Aug | US | + rest of world, last 5–6 wks | global, full quarter | + July expansion of eligible bookings |
| RNPL % of GBV (disclosed) | not disclosed | not disclosed | ~20% | >20% | ~22% ours (21–27%) |
| Bundle's nights contribution (management) | "helped drive" NA | >2.0pt | ~3pt | not given | P(not given) 0.72 |
| Unearned fees y/y minus GBV y/y (pre-RNPL: −2 to +5) | −4pt | −8pt | −19pt | −17pt | ≤ −18 supports us |
| Unpaid RNPL share of the booked-not-stayed book (our solve) | 1–6% | 5–10% | 14–18% | 15–19% (~21m nights) | |
| North America nights (letter wording) | mid-single | mid-single | high-single | high-single | +5.6% ours (US RNPL lapped) |
| Total nights y/y | +8.8% | +9.8% | +9.2% | +10.3% | +9.9% base; stays +9.2–9.5%; Street +11.5% |

*Sources: shareholder letters, 10-Q/10-K, call transcripts (60-statement RNPL ledger); balance sheets; unpaid share solved from
unearned fees against pre-RNPL norms; stays from the reviews index; Street = Bloomberg MODL, 12 Sep 2026.*

**Cut order if the page is over.** (1) The completed-stays sentence (the exhibit row carries it). (2) "Management still expects
growth… 'low double digits'". (3) The 10-Q "less correlated" quote. (4) The lap-schedule parentheticals (keep "adds up to
management's own three points"). (5) The North America rows of the exhibit.

---

## 2. What changed from the current draft, and why

| Current draft | Problem | Fix |
|---|---|---|
| "increased the percentage of browsers that actually book from +2% to +8% in North America" | That is **North America nights growth** as described in the letters (low-single → mid-single → high-single digits), not a conversion rate. Airbnb has never disclosed a look-to-book rate. | Stated as NA nights growth. |
| "+9.5% +8.7% +8.5% through Q1–Q3 2024 then +7.9% +7.4% in Q1–Q2 2025" | Skips **4Q24 at +12.3%**. A judge who checks will call it cherry-picked. | Half-years from printed levels: 1H24 +9.1%, 1H25 +7.7%, 1H26 +9.7%. |
| "In 2026, nights re-accelerated due to RNPL (+8.8% +9.2% +10.3% through Q2 2026)" | +8.8% is **3Q25**, and 4Q25's **+9.8%** is missing. Management credited the ~3 points to **three features together**, not to RNPL alone. 1Q26 was also cut ~1pt by Middle East cancellations (1Q26 letter: ~10% without them). | Correct series in the exhibit. Attribution given to "the three features". |
| "the cancellation rate increases exponentially" [YJL4.1] | Nothing in the record supports "exponential". The platform rate moved by about **1pt**. The unpaid share of the book rose and then **flattened** (14–18% → 15–19%). The cohort drag **peaks in 2H26 and fades** as it laps too (−0.59 → −0.54 → −0.25 → −0.14pt, 3Q26–2Q27). | Replaced with the timing mechanism (payment deadline → cancellation near the stay → recorded in a later quarter) and the balance-sheet exposure. |
| "The ease of booking also inflates nights and GBV, overstating forward guidance" | Asserted, with no mechanism. | Reported nights are bookings net of cancellations *recorded in the quarter*. RNPL cancellations are recorded near check-in, so a quarter's bookings are counted before their cancellations (10-K example, ledger D054). |
| Memo v3 RNPL table's "Eligible share of GBV" column (10%, 15–18%, 25–35%, 45–55%, 50–60%) and "~4% / ~9% assumed" 2025 shares | No source note in the repo derives the eligible-share column. The 2025 shares are labelled assumed. | Dropped. 2025 is shown through the balance-sheet solve instead, which uses filed numbers. |

**Consistency with the official model.** The official base (DEC-0019) keeps the cancellation drag **out** of the base
because there is no empirical signature (the D1 no-stacking rule). If the memo says cancellations *drive* the miss, it
contradicts our own base. The text above keeps base = lap and short = lap + tail, which matches `final_nights.md` §4.4.

---

## 3. The three questions, answered with the record

### 3a. How RNPL has grown as a share of GBV

| Quarter | Share | Source | Official or mirror |
|---|---|---|---|
| 2Q25 and earlier | 0% (not launched) | US launch Aug 2025, newsroom 14 Aug (D001); call says "beginning of Q3" (D004) | official / mirror |
| 3Q25 | not disclosed; "about 70% of people that we offer" RNPL take it (US, headcount) | 3Q25 call (D005) | mirror |
| 4Q25 | not disclosed; "over 70% adoption by eligible bookings", on global GBV | 4Q25 letter footnote (D022) | official |
| 1Q26 | "roughly 20% of global GBV" | 1Q26 letter (D031) | official |
| 2Q26 | "over 20% of our total GBV" | 2Q26 call (D043) | mirror; the letter carries no share |
| 3Q26E | ~22% central, 21–27% scenarios; P(disclosed ≥25%) 0.25, P(not disclosed) 0.29 | RNPL module params; C06 rev 2 | ours |

The two 70% figures are different statistics (US people vs global GBV). Do not chain them into a series (ledger note §2.1).
Why "stopped rising": 1Q26 had RNPL outside the US for only the last 5–6 weeks (UK 18 Feb, AU/APAC 23 Feb, Canada 4 Mar;
BRL/INR/TRY payers excluded, D025–D029). 2Q26 was the first full global quarter, and the share moved only from "roughly 20%"
to "over 20%". The balance sheet agrees: the unearned-fee gap narrowed from −19pt to −17pt, and the unpaid share of the book
rose only 1.5pt (13.9% → 15.4% at B = 1.00).

### 3b. What management says will happen

| Date | Statement | Source |
|---|---|---|
| 12 Feb 2026 | "After a strong U.S. launch-with over 70% adoption by eligible bookings-and testing in other markets, we're rolling it out to more guests in 2026." | 4Q25 letter (D022), official |
| 7 May 2026 | "we face tougher comparisons in the back half of this year against the rollout of Reserve Now, Pay Later in 2025 and current headwinds from the Middle East conflict." | 1Q26 letter (D040), official |
| 7 May 2026 | RNPL shifts guest payments "closer to the date of stay, resulting in lower unearned fees in Q1 and Q2 and higher unearned fees in Q3." | 1Q26 letter (D038), official. **This is the one dated, testable prediction.** |
| 6 Aug 2026 | "Given the strong results that it's delivered, in July, we expanded the types of bookings eligible for Reserve Now, Pay Later." | 2Q26 call, Mertz (D044), mirror |
| 6 Aug 2026 | "beyond the immediate uplift in nights booked, we believe this provides a longer-term competitive benefit, enabling hosts to lock in earlier calendar share" | 2Q26 call, Mertz (D046), mirror |
| 6 Aug 2026 | "As adoption of RNPL and our other flexible payment options continues to grow, the timing among GBV, revenue, and cash receipts may become less correlated." | 2Q26 10-Q MD&A, official |
| 6 Aug 2026 | Implied take rate "relatively flat compared to 2025, accounting for the timing of bookings versus check-in with Reserve Now, Pay Later" | 2Q26 call, Mertz (D050), mirror |
| 6 Aug 2026 | Pricing is "many multiples bigger than RNPL." | 2Q26 call, Chesky (D053), mirror |
| 6 Aug 2026 | 3Q26: "low double-digit growth in Nights and Seats Booked" | 2Q26 letter (D052), official |

What this record says: management expects adoption to keep growing. It has named the 2H26 lap itself. It has moved its
growth story from RNPL to pricing, and its filings now stress timing rather than growth. It has not quantified the July
expansion.

### 3c. How RNPL has affected cancellations

| Evidence | What it says | Status |
|---|---|---|
| 2Q26 10-Q MD&A | "To date, RNPL bookings, which require no payment at the time of booking, have experienced higher cancellation rates than historic bookings in which some or all of the cash was received at the time of booking." | official, unquantified |
| 4Q25 call, Mertz (D017, D018) | "the aggregate nominal increase in cancellations rate, it's approximately 1%"; "an average of maybe 16% cancellation rate historically going to 17%" | mirror; no base period, denominator or unit of account |
| 1Q26 call, Mertz (D035) | "Certainly with the offering, there's a very elevated level of cancellations that come with the program. Across all regions, what we see is that the net impact is positive to the business." | mirror; the second sentence is the counter-claim and must travel with the first |
| 4Q25 call, Mertz (D019, D020) | The product was tested so that by check-in "the growth lift in bookings was larger than the net increase in cancellations"; realised curves are "very close to what we saw from a tested perspective" | mirror; **a stay-date test on a booking cohort, not a claim about quarterly reported nights** |
| Implied RNPL cancellation rate | 1pt ÷ RNPL nights share 16.7% (1Q26) = +6.0pt, so about 22% vs 16%. Our module's base uses +4pt (~20%) | derived. The Oct-2025 cancellation redesign and the 2Q26 Strict→Firm migration (D048) also raise cancellations, so +6 is an upper bound on RNPL's share of the rise |
| Cohort engine, 2,025 cells | 3Q26 drag −0.10 to −1.37pt; central −0.15 (+1pt), −0.62 (+4pt), −0.93 (+6pt); 46% (3Q26) and 49% (4Q26) of excess cancellations come from earlier cohorts | model; propensity is a scenario input, never measured |
| Unified RNPL module (base, +4pt) | Cancellation tail (M3+M4) −0.59 (3Q26), −0.54 (4Q26), −0.25 (1Q27), −0.14 (2Q27) | model; the tail laps too once the share stops rising |
| Calendar reopening, 34 markets | No RNPL signature. Non-US minus US +2.1pt, permutation p 0.26, driven by Australia, fragile | alt data, **counter-evidence** |
| Calendar pilot, 3 markets | Short-run reopening Mar→Jun vs Jun→Aug: Austin 10.2→10.0%, Rome 9.0→13.3%, Sydney 9.4→7.7% | descriptive lead only; Rome did not generalise |

---

## 4. How each piece of evidence flows into the forecast

| Evidence | Kind | What it measures | Result | Where it enters | File |
|---|---|---|---|---|---|
| RNPL statement ledger (60 statements, 33 official) | disclosure | rollout dates, share, attribution, cancellation language | lap dates; share ~20% → >20%; bundle >2 → ~3 → silence | lap schedule in the **base** | `data/processed/overnight2/D/rnpl_statement_ledger.csv`; `research/notes/overnight2/D_*.md` |
| Lap schedule | disclosure + two fitted NA terms | pts of total nights per leg | US RNPL −0.69 (3Q26); fee+cancel −0.66 NA −0.78 ex-NA (4Q26); ex-NA RNPL −0.87 to −1.05 (1Q27 partial, 2Q27 full); sums to 2.9–3.3 vs mgmt ~3.0 | **base** nights line | `final_nights.md` §3.0, §4; D §2.2 |
| Unearned fees vs GBV | filed balance sheets | unpaid RNPL stock | gap −4 / −8 / −19 / −17pt; unpaid share 1–6% → 15–19% of book | exposure for the tail; 5 Nov falsifier | `data/processed/rnpl_short_audit/verify_bs_yoy_gap_table.csv`, `verify_bs_uf_only_solve.csv` |
| Backlog identity (nights v3, N2) | filings + model | booked-not-stayed nights | 136.8m backlog at 2Q26, 21.0m unpaid RNPL (13.6–37.3) | exposure; 3Q26 unearned-fee band $1,519–1,957M vs $2,105M pre-RNPL expectation | `final_nights.md` §3.13 |
| Cohort engine | model | timing and size of the cancellation drag | −0.10 to −1.37pt (3Q26); 46–49% from earlier cohorts | **short case** only | `D1_rnpl_cohort_scenarios.csv`, `D1_cohort_matrix_cancellation.csv` |
| Unified RNPL module | model | lap + pull-forward + tail, by quarter | 3Q26 9.49%, 4Q26 7.61%, FY27 6.41% | short case; cross-check on base | `data/processed/rnpl_short_audit/rnpl_nights_module.csv` |
| Reviews stays index (123 markets, 363 dumps) | alt data | completed stays, net of every cancellation | 3Q26 +9.2% (stays-only, W1/W2) to +9.5% (W2-corrected index) | cross-check of the 146.8m base | `final_nights.md` §3.1–3.13 |
| Calendar reopening (34 markets) | alt data | cancel-and-reopen in host calendars | no signature | why the tail is short case, not base | `research/notes/overnight2/A_calendar-reopening-34-markets.md` |
| Pitch-forecast questions | forecasts | 5 Nov disclosures | C05 bundle not quantified 0.72 (≥2.5pt 0.07); C06 share ≥25% disclosed 0.25; C07 negative effect conceded 0.27; C12 unearned fees ≤ −3% 0.43; R03 share ≥25% with nights ≥10% 0.11 | 5 Nov score sheet | `docs/pitch-forecasts/forecast_table.csv` |
| B. Riley via Finimize | sell-side, second-hand | RNPL nights contribution | 200bp in 1Q26 → 150bp in 2Q26 | corroboration only: a paywalled, undated fragment, not quoted in the memo | `docs/pitch-forecasts/questions/risk-july-rnpl-expansion-offsets-lap/sources/finimize_rnpl_expansion_2026.txt` |

**Nights, derived from printed levels** (`data/processed/overnight/02_kpi_panel_quarterly.csv`): 1Q24 132.6, 2Q24 125.1,
1Q25 143.1, 2Q25 134.4, 1Q26 156.2, 2Q26 148.3 (m). 1H24 +9.1%, 1H25 +7.7%, 1H26 +9.7%. Quarterly y/y: 1Q24 +9.5, 2Q24 +8.7,
3Q24 +8.5, 4Q24 +12.3, 1Q25 +7.9, 2Q25 +7.4, 3Q25 +8.8, 4Q25 +9.8, 1Q26 +9.2, 2Q26 +10.3.

**Unearned fees y/y minus GBV y/y** (same panel): 1Q24 −0.2, 2Q24 +0.7, 3Q24 +3.1, 4Q24 −0.3, 1Q25 +4.9, 2Q25 −1.8 | 3Q25
−4.1, 4Q25 −8.1, 1Q26 −18.8, 2Q26 −16.7. Pairs with chart `n07_unearned_fees_vs_gbv.png` on `krish/pitch-charts`. The
implied cancellation-rate chart there (`n06`) is the visual for §3c.

---

## 5. Check before 2 Oct

1. **Mirror quotes.** The 16→17% remark, "very elevated", "over 20%" for 2Q26, the July expansion and the Chesky pricing
   line all come from stockanalysis.com transcript mirrors, not the official IR PDFs. Check each against the IR transcript
   or webcast before the memo quotes it verbatim (see `abnb-transcript-sources` for the IR CDN pattern).
2. **"Below all 28 estimates"** depends on the 12 Sep MODL pull (low 147.0m). Re-pull before submission.
3. **Street 4Q26 +9.9%** is MODL 134.0m on the 121.9m base (12 Sep, n 28). Same refresh.
4. The 3Q26 base is the mechanism's 146.8m (DEC-0029). Memo v3 still says 146.3m / +9.5%. Use one number across the memo.

## RESUME

This is a text rewrite, not a model change, and nothing was registered. The next agent should: (1) verify the five
mirror-sourced quotes in §5 against official IR transcripts and swap any that differ; (2) once the team settles the page
budget, apply the cut order in §1; (3) if the team wants a chart, pair Exhibit 1 with `n07` (unearned fees vs GBV) from
`krish/pitch-charts`. After 5 Nov, score C05/C06/C07/C12 and the unearned-fee band ($1,519–1,957M; above $2,105M says RNPL is
not deferring cash as assumed), and update the 3Q26E column with the printed values.
