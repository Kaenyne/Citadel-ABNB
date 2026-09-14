# 05a — The cash-reality object: what Airbnb actually collects, once RNPL timing is handled

- **Date:** 2026-09-11. **Author:** Opus build agent for Theo.
- **Object:** #2 in `docs/superpowers/specs/2026-09-11-rnpl-quality-of-growth-study-design.md`.
- **Script (new):** `analysis/src/rnpl_short_audit/qog_cash_reality.py`. Run from the repo root. No network, no writes outside `data/processed/rnpl_short_audit/`.
- **Data (new):** `data/processed/rnpl_short_audit/qog_cash_reality_*.csv` (ten files, listed at the end).
- **Read, read-only:** `data/processed/overnight/02_kpi_panel_quarterly.csv`; `data/processed/abnb_fcf_bridge.csv`; `data/raw/regulatory/quantification/abnb_2025_10k.json` and `abnb_2026q2_10q.html`; `docs/rnpl-short-audit/01`, `04`; `research/notes/overnight2/D_rnpl-statement-ledger-and-cohort-scenarios.md`; `data/processed/overnight/02_guidance_ledger.csv`, `13_model_annual.csv`, `29_fy27_bridge.csv`.
- **Nothing existing was modified.** Every number carries **measured / derived / assumed**.
- The struck series are not used: no "restated unearned fees" pin, no −3.4pp FX step, no "82% determined", no +4.05% fee uplift, no 9/9 drift rule, no "half of ADR is unit size", no "+10.2% consensus".

---

## 1. Bottom line

1. **Strip the float and cash conversion has not deteriorated — it improved.** FCF ex-float (CFO − Δunearned fees − capex) grew **+24.4% in 1H26 against revenue +17.1%**, and its margin rose from 28.0% to 29.7%. Reported FCF grew +7.8%. The entire gap between the headline FCF slowdown and the top line is the float. *(derived)*

2. **The RNPL cash drag is $469m cumulative to 30 June 2026, and it is a Q1–Q2 phenomenon.** Against the pre-RNPL seasonal norm the unearned-fees stock is short **$466m at 2Q26**. Quarter by quarter the FCF drag is **3Q25 −$30m, 4Q25 −$75m, 1Q26 −$340m, 2Q26 −$24m**. The same construction run over eight pre-RNPL quarters, where the true drag is zero, has a standard deviation of **$39m** and a worst case of $64m — so **only 1Q26 is outside the noise** (8.7σ). 4Q25 and 2Q26 are not separately identified. *(derived)*

3. **From 3Q26 the transition reverses the sign and becomes a tailwind to reported FCF growth.** Q3 is the quarter in which the deferred summer book is collected: the shortfall falls from $466m (30 June) to ~$306m (30 Sept, central), which is **+$160m of cash into 3Q26** and **+$189m of year-on-year help to 3Q26 FCF growth**. Management said this in advance — 1Q26 letter (ledger D038): RNPL "results in lower unearned fees in Q1 and Q2 and higher unearned fees in Q3". The y/y help continues at +$64m (4Q26), +$64m (1Q27), +$12m (2Q27) on the central path. *(derived; the forward path is assumed)*

4. **The permanent effect is small and is bounded by the interest yield, exactly as the study design warned.** The 2027 bridge below puts the whole recurring RNPL cost at **−$106m of FCF, 0.7pp of margin** (bear −$133m, bull −$51m), of which the float-interest term is **−$29m** (range −$11m to −$98m). This object does **not** support "the cash never arrives"; it supports "the cash arrives later, permanently costs the interest on it, and the Street's FCF-per-share extrapolation off a booking-quarter KPI is mis-timed."

5. **The single-fee migration adds no float.** The FY2025 10-K puts the host fee in unearned fees at cash receipt under *both* fee structures. This reproduces `docs/rnpl-short-audit/04` §C2 independently and removes term (c) from the bridge. *(measured)*

6. **The 5 November FCF test as pre-registered is mis-specified for Q3.** Expected 3Q26 FCF is **$1,554–1,762m at a 33.1–36.9% margin**, i.e. *above* the 3Q25 print of $1,349m / 32.9%, on the central RNPL path and the guided revenue range. A 3Q26 FCF margin at or above 32.9% is **not** evidence against the thesis. The discriminating line on 5 November is the unearned-fees stock; the discriminating FCF quarter is **1Q27**. Corrected rule in §6.

7. **Honest framing for the deck:** trailing-four-quarter FCF is still growing — **+12.9% against TTM revenue +13.6%** at 2Q26 (the brief's "+13% vs +15%" is the same fact at a slightly different revenue vintage). This is a conversion-and-timing story, not a collapse.

---

## 2. Exhibit — KPI momentum against cash conversion, same-quarter y/y

`qog_cash_reality_exhibit.csv`. All growth rates are same-quarter y/y because the 10-Q seasonality
paragraph forbids sequential reading. Nights and GBV are **measured**; FCF ex-float is **derived**.

| Quarter | Nights | GBV | Revenue | Adj. EBITDA | **FCF** | **FCF ex-float** | FCF margin | FCF ex-float margin |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1Q24 | +9.5% | +12.3% | +17.8% | +61.8% | +20.7% | +52.6% | 89.1% | 42.1% |
| 2Q24 | +8.7% | +11.0% | +10.6% | +9.2% | +15.9% | +18.1% | 38.0% | 31.1% |
| 3Q24 | +8.5% | +9.8% | +9.9% | +6.8% | −18.0% | −6.9% | 28.8% | 54.6% |
| 4Q24 | +12.3% | +13.5% | +11.8% | +3.7% | +895.7% | +480.2% | 18.5% | 20.1% |
| 1Q25 | +7.9% | +7.0% | +6.1% | −1.7% | −6.7% | −25.3% | 78.4% | 29.7% |
| 2Q25 | +7.4% | +10.8% | +12.7% | +16.7% | −7.8% | −3.3% | 31.1% | 26.7% |
| **3Q25** | +8.8% | +13.9% | +9.7% | +4.7% | +25.6% | +17.1% | 32.9% | 58.3% |
| **4Q25** | +9.8% | +15.9% | +12.0% | +2.7% | +13.8% | +19.8% | 18.8% | 21.5% |
| **1Q26** | +9.2% | **+19.2%** | +17.9% | +24.5% | **−4.3%** | +5.9% | 63.6% | 26.7% |
| **2Q26** | +10.3% | +15.7% | +16.5% | +20.9% | +30.2% | +39.5% | 34.7% | 32.0% |

Read it as: GBV accelerates from +7.0% (1Q25) to +19.2% (1Q26) while reported FCF goes from −6.7%
to −4.3%; but **FCF ex-float goes the other way**, from −25.3% to +5.9%. The 1Q26 cell is the
exhibit. 4Q24's +895.7% is a base artefact (4Q23 FCF was $46m) and should be footnoted, not shown.

**Half-year, the only RNPL-era period with a published cash-flow statement** (`qog_cash_reality_annual.csv`):

| | Revenue | CFO | Δ unearned fees | Capex | FCF | FCF margin | **FCF ex-float** | **ex-float margin** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1H2025 | $5,368m | $2,764m | +$1,241m | $21m | $2,743m | 51.1% | $1,502m | 28.0% |
| 1H2026 | $6,286m | $2,978m | +$1,088m | $21m | $2,957m | 47.0% | $1,869m | 29.7% |
| y/y | **+17.1%** | +7.7% | −$153m | — | **+7.8%** | −4.1pp | **+24.4%** | **+1.7pp** |

Δ unearned fees is the balance difference; it reconciles to the cash-flow-statement line within
**$3–11m** over five published periods (`qog_cash_reality_uf_reconciliation.csv`): FY23 +3, FY24
−11, FY25 +5, 1H25 +5, 1H26 +3. *(measured both sides)*

**Seasonality, so the y/y comparisons stay same-quarter** (`qog_cash_reality_seasonality.csv`,
mean FCF margin): 1Q 77.0%, 2Q 34.6%, 3Q 30.9%, 4Q 18.6% over 1Q24–2Q26. The 10-Q: *"FCF is
typically highest in the first quarter and lowest in the fourth quarter."* Mean Δ unearned fees
runs +$1,035m (Q1), +$140m (Q2), −$1,001m (Q3), −$59m (Q4). Mean **ex-float** margin is 32.8 / 30.0
/ 56.4 / 20.8% — the float is the whole of the Q1-versus-Q3 difference in headline FCF.

**SBC-adjusted** (full series in `qog_cash_reality_quarterly.csv` and `_annual.csv`): FY2025
FCF − SBC $3,032m (70.6% of adj. EBITDA, from 75.4% in FY2024); FCF ex-float − SBC $2,905m.
2Q26 FCF − SBC $766m, FCF ex-float − SBC $668m.

**Interest income and the customer-funds share** (`qog_cash_reality_quarterly.csv`):
FY23 $721m, FY24 $818m, FY25 $705m, 2Q26 $183m — all **measured**. The share attributable to
customer float is **derived**: average (funds payable + unearned fees) over average (cash +
short-term investments + restricted cash + funds held on behalf of customers), applied to the
interest-income line. FY2025 **$382m of $705m (54%)**; 1H26 **$194m of $338m (57%)**; 2Q26 $110m
of $183m (60%). The blended implied yield is 3.56% (FY25) and 3.09% (1H26) annualised — **assumed
as the customer-funds yield, because none is disclosed** (§5).

---

## 3. The RNPL transition, isolated

`qog_cash_reality_transition.csv`. Method: the pre-RNPL norm is the unearned-fees stock over
**next-quarter** revenue, rebuilt in the script over pre-RNPL quarters from 1Q23 to 2Q25 and
asserted against the study's pins — 1Q **0.8799** (pin 0.880), 2Q **0.6970** (0.697), 3Q **0.6648**
(0.665), 4Q **0.6887** (0.689). Shortfall = norm − actual. **The FCF effect in a quarter is the
change in the shortfall, not its level.**

| Quarter | UF actual | UF at norm | **Shortfall** | % of norm | **FCF drag in quarter** | FCF reported | FCF ex-RNPL | FCF y/y − revenue y/y |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1Q25 | $2,723m | $2,724m | $1m | 0.0% | −$52m | $1,781m | $1,833m | −12.8pt |
| 2Q25 | $2,857m | $2,854m | −$3m | −0.1% | +$4m | $962m | $958m | −20.4pt |
| **3Q25** | $1,820m | $1,847m | **$27m** | 1.4% | **−$30m** | $1,349m | $1,379m | +15.9pt |
| **4Q25** | $1,743m | $1,844m | **$101m** | 5.5% | **−$75m** | $521m | $596m | +1.7pt |
| **1Q26** | $2,733m | $3,175m | **$442m** | 13.9% | **−$340m** | $1,704m | $2,044m | **−22.2pt** |
| **2Q26** | $2,831m | $3,297m | **$466m** | 14.1% | **−$24m** | $1,253m | $1,277m | +13.7pt |

- 2Q26's norm uses the guided 3Q26 revenue midpoint ($4,730m; 2Q26 letter) because 3Q26 is not
  reported. At the guide low/high the 2Q26 shortfall is $437m / $493m. *(derived on a measured guide)*
- **Noise band.** Over 3Q23–2Q25 the same drag construction has mean +$3m, sd **$39m**, |max| $64m.
  So −$340m (1Q26) is real; −$75m (4Q25) and −$24m (2Q26) are inside the band and must not be
  quoted as separately identified. The **cumulative** $466m at 2Q26 is 12σ and is the number to use.
- Quarterly FCF growth minus revenue growth is a **noisy line and cuts both ways** (+15.9, +1.7,
  −22.2, +13.7 from 3Q25). The stable statement is the trailing four quarters: **−0.7pt at 2Q26**
  (FCF +12.9%, revenue +13.6%), from −8.5pt at 1Q26.
- **The $466m is the fee slice only.** `docs/rnpl-short-audit/04` puts the unpaid book at
  $3.3–6.9bn of GBV at 30 June. At a ~13.3% realised take rate, only ~$440–920m of that is
  unearned fees; the other ~87% is host money, which sits in funds payable and **the 10-K excludes
  funds payable from FCF**. The headline unpaid book is 7x the FCF-relevant number. Do not conflate.

---

## 4. The 2027 permanent-effect bridge

`qog_cash_reality_bridge_2027.csv`. Share path: **central 22% of GBV in 3Q26, 23% in 4Q26, 25%
through 2027; bear 30%; bull 20%** (assumed; history measured — ~20% in 1Q26 per the 1Q26 letter,
ledger D031, ">20%" in 2Q26 per the 2Q26 call, D043). Base FY27 revenue $15,842m and GBV $118,081m
from `data/processed/overnight/13_model_annual.csv` Base 2027 (derived).

| # | Term | Central | Bear | Bull | Status |
|---|---|---:|---:|---:|---|
| A | **FCF 2027 if RNPL did not exist** | **$6,031m** | $6,031m | $6,031m | **derived** |
| B | Transition: RNPL share still stepping up (23%→25%) | −$65m | −$87m | −$17m | **derived** |
| C | Permanent: interest income on float never collected | −$29m | −$35m | −$24m | **derived** on an **assumed** yield |
| D | Permanent: +1pt platform cancellation rate, processing cost | −$11m | −$11m | −$11m | **derived** |
| E | Single-fee migration working capital | **$0m** | $0m | $0m | **measured** |
| F | **FCF 2027 with RNPL** | **$5,925m** | $5,898m | $5,980m | **derived** |
| | Total RNPL cost | −$106m (0.7pp) | −$133m | −$51m | |

- **A** = the FY2025 realised ex-float conversion (36.6%) applied to base FY27 revenue, plus the
  pre-RNPL seasonal change in unearned fees over the year (+$225m). It is *not* a house FY27 FCF
  forecast: the repo base model lands at $5,420m with its own P&L assumptions. Applying the same
  RNPL deltas there gives **$5,314m** (memo row). Only the deltas belong to this object.
- **B** is the residual transition. Once the share plateaus the level of deferred cash stops
  growing and the drag disappears — which is why B is an order of magnitude below the 1Q26 quarter.
- **C, float loss:** central **$956m** of average customer float never collected in FY2027, range
  **$365m–$2,757m**. Low bound = the measured unearned-fees shortfall only (FX-clean). Central =
  that plus the measured ex-FX funds-payable lag at 2Q26 (3.8pt of a $11,067m base, from
  `docs/rnpl-short-audit/04`), converted to a four-quarter average and scaled to FY27 volume and
  share. High bound = the unpaid share applied to the whole customer backlog, i.e. the unpaid-GBV
  reading. At an **assumed** 3.09% blended yield the interest lost is **−$29m (range −$11m to
  −$98m)**; at the FY25 yield of 3.56% the central is −$34m. *The permanent float cost is a
  rounding error on a $6bn FCF base and must be quoted as such.*
- **D:** a 1-point rise in the platform cancellation rate on FY27 volume is ~$1,423m of extra
  cancelled GBV. At the **derived** merchant-fee rate of **1.52% of pay-in volume** (§5) that is
  **−$22m if every incremental cancellation happens after payment and $0 if before**. RNPL
  cancellations land days before check-in and, by construction, often before the payment date, so
  the central is half: **−$11m**. Memo, not in the bridge to avoid double counting: the same point
  is ~**$189m of revenue** at a 13.25% take rate — that belongs to the KPI-inflation object.
- **E = $0.** FY2025 10-K Note 2: *"Host and guest fees are recorded as cash with a corresponding
  amount in unearned fees"*, and *"For all bookings, the guest pays the booking amount to the
  Company, which disburses the booking amount to the host after check-in, net of the host's service
  fees."* The host fee is collected at booking under the split-fee structure too, so the migration
  creates no float. The only effect is a one-time stock build on the higher total take, which lands
  in 2026 as the migration completes, not in 2027.

---

## 5. Filing language, verbatim, with location

`qog_cash_reality_filing_facts.csv` carries all twelve with their quotes.

**FCF definition and the float exclusion** — FY2025 10-K (`data/raw/regulatory/quantification/abnb_2025_10k.json`) p.43, Item 7, "Free Cash Flow Reconciliation". The reconciliation itself is *net cash provided by operating activities* less *purchases of property and equipment*; FY2025 $4,646m − $33m = $4,613m, 38% margin. No other adjustment.

> "Our FCF is impacted by the timing of GBV because we collect our service fees at the time of booking, which is generally before a stay, experience, or service occurs. Funds held on behalf of our customers and amounts payable to our customers do not impact FCF, except interest earned on these funds."

2Q26 10-Q (`abnb_2026q2_10q.html`), Part I Item 2, "Free Cash Flow Reconciliation" — the amended version:

> "Our FCF is impacted by the timing of GBV, as we generally collect our service fees at booking, which typically occurs before a stay, experience, or service. For bookings under RNPL, we collect payment closer to the date of stay. The continued expansion of RNPL results in a shift in timing of when cash for unearned fees is received, which impacts our FCF. Funds held on behalf of customers and amounts payable to customers do not impact FCF, except for interest earned on those funds."

**Interest-income line** — FY2025 10-K p.46–47, Item 7, "Interest Income"; consolidated statements of operations p.55. **FY2023 $721m, FY2024 $818m, FY2025 $705m** (measured).

> "Interest income consists primarily of interest earned on our cash, cash equivalents, marketable securities, and amounts held on behalf of customers."

2Q26 10-Q, Part I Item 2, "Interest Income": 2Q26 **$183m** vs 2Q25 $190m; 1H26 **$338m** vs 1H25 $363m (measured).

> "Interest income decreased by $7 million, or 4%, and $25 million, or 7%, respectively, primarily due to lower interest earned on our investment portfolio, driven by lower interest rates, partially offset by a slight increase in interest income on operating cash."

**Payment-processing share** — FY2025 10-K p.85, Note 16 significant-segment-expenses table:
**merchant fees and chargebacks FY2023 $1,369m, FY2024 $1,508m, FY2025 $1,666m** (measured) —
**1.82% of FY2025 GBV, 1.52% of pay-in volume** grossed up at a 17% cancellation rate (derived).
Cost of revenue FY2025 $2,086m, 17% of revenue (measured). p.45, Item 7:

> "Cost of revenue includes payment processing costs, including merchant fees and chargebacks, costs associated with third-party data centers used to host our platform, and amortization of internally developed software and acquired technology. As the merchant of record, we bear all payment processing costs for our bookings, including those from chargebacks due to both fraud and non-fraud activities."

and, on the FY2025 move: *"Cost of revenue increased $208 million, or 11%, primarily due to a $188 million increase in merchant fees, due to higher pay-in volumes."*

**Refunds** — 10-K p.63, Note 2: *"The Company accounts for refunds, net of any recoveries, as variable consideration, which results in a reduction to revenue. … The estimate for variable consideration was immaterial as of December 31, 2024 and 2025."* So the refund *cost* line is immaterial in the filings; the cancellation cost is a revenue effect plus the processing term in D.

**Customer-funds yield — NOT DISCLOSED.** Interest income is presented as a single line covering
corporate cash, marketable securities and customer funds together (10-K p.46–47). No segregated
yield, no average-balance table. The object therefore uses the **blended implied yield** — interest
income over the average of cash, short-term investments, restricted cash and funds held on behalf
of customers — at **3.56% (FY2025)** and **3.09% (1H2026)**, and labels every number that depends
on it **assumed**. This is the single largest soft input in §4 term C.

**RNPL cancellation and correlation** — 2Q26 10-Q, Part I Item 2, "Gross Booking Value":

> "To date, RNPL bookings, which require no payment at the time of booking, have experienced higher cancellation rates than historic bookings in which some or all of the cash was received at the time of booking. As adoption of RNPL and our other flexible payment options continues to grow, the timing among GBV, revenue, and cash receipts may become less correlated."

**RNPL cash mechanics** — 2Q26 10-Q, "Liquidity and Capital Resources": *"under our RNPL option, payment is collected closer to check-in rather than at booking. Accordingly, unearned fees are not recorded, and operating cash flows are not generated until payment is received."*

---

## 6. The 5 November test for this object

`qog_cash_reality_3q26_test.csv` and `qog_cash_reality_forward_drag.csv`. 3Q26 guidance is
**measured**: revenue $4.69–4.77bn (+15–17%), GBV mid-teens, nights low double digits
(2Q26 letter, `data/processed/overnight/02_guidance_ledger.csv`). FCF is built as
**FCF = FCF ex-float + Δ unearned fees**, with the Q3 ex-float conversion taken from the last two
Q3s (56.5%) and the last four (59.1%).

| 3Q26, central path (22% of GBV) | Expectation |
|---|---|
| Unearned fees, 30 Sep 2026 | **$1,762m, −3.2% y/y** (pre-RNPL norm $2,068m, +13.6%) |
| Δ unearned fees in the quarter | −$1,069m (3Q25: −$1,037m) |
| **FCF** | **$1,582–1,748m** (all cells $1,554–1,762m) |
| **FCF margin** | **33.7–36.7%** (all cells 33.1–36.9%) |
| 3Q25 print | $1,349m, 32.9% |

**Reading rule.**

1. **A 3Q26 FCF margin at or above 32.9% is not evidence against the thesis, and must not be
   scored as such.** Q3 is the collection quarter for the deferred spring/summer book; the central
   path puts **+$160m of RNPL cash into 3Q26** and **+$189m of y/y help to FCF growth**. Management
   pre-announced it (1Q26 letter, D038). The pre-registered cash test's FCF-margin leg is
   mis-specified for a third quarter and should be re-pointed at 1Q27.
2. **The discriminating line on 5 November is the unearned-fees stock**, and the rule is the one
   already carried in `docs/rnpl-short-audit/04` §C4: score **(3Q26 unearned fees y/y) − (3Q26 GBV
   y/y)**. At or below **−18pt** supports; **−12 to −18pt** in line with 1H26; wider than **−8pt**
   weakens. In levels on this object's norm: **$2,068m is the no-RNPL mark; $1,762m is central;
   $1,734m is bear; $1,776m is bull.**
3. **FCF cells that do carry information.** Below **$1,500m / 32%** on guided revenue means the
   deferral is deeper than a 22% share implies — strong support, and it would also require the
   unearned-fees line to print below $1,700m. Above **$1,800m / 37%** *with* unearned fees above
   $1,900m means the book is unwinding faster than modelled — weakens the drag hypothesis.
4. **Cross-check, not a trigger:** the cash-flow statement's "Unearned fees" line against the
   balance move. They have agreed within $3–11m over five published periods; a divergence is an
   accounting change, not RNPL.
5. **The decisive FCF quarter is 1Q27, reported in February 2027**, because the drag concentrates
   in the booking-heavy quarter (1Q26 was −$340m). Even there the central path has the drag
   *shrinking* year on year (−$276m vs −$340m), so the test is on the **level of the shortfall**
   ($593m central, $711m bear at 30 Mar 2027), not on FCF growth.

---

## 7. Method

- Panel from `02_kpi_panel_quarterly.csv`; interest income from `abnb_fcf_bridge.csv`, verified
  against the filings (2Q25 $190m, 2Q26 $183m, 1H25 $363m, 1H26 $338m, FY24 $818m, FY25 $705m all
  tie exactly).
- FCF ex-float = CFO − Δ unearned fees − capex; Δ unearned fees is the balance difference, with the
  cash-flow-statement line carried as a reconciliation (§2). The funds-payable FX reconciliation
  problem does not touch unearned fees, which is FX-clean.
- Interest income on customer funds = interest income × [average (funds payable + unearned fees) ÷
  average (cash + short-term investments + restricted cash + funds held on behalf of customers)].
  Equivalent to average customer balances × the blended implied yield. **Derived.**
- Seasonal norm rebuilt in code and asserted against the study's pins to within 0.002.
- Drag in quarter t = −(shortfall_t − shortfall_{t−1}); the noise band comes from running the same
  construction over eight pre-RNPL quarters where the answer is known to be zero.
- 2027 pass-through from RNPL GBV share to the unearned-fees shortfall rate is pinned on 2Q26
  (14.1% of norm at a measured ~21% share → 0.67) and applied linearly to the share path. Linearity
  is **assumed** and is the second-largest soft input after the yield.

---

## 8. What this object can and cannot identify

**Can.** (i) The size and quarterly shape of the RNPL cash-timing effect, to a ±$39m one-quarter
noise band and ±12σ on the cumulative. (ii) That ex-float conversion has *improved*, which
falsifies any version of the thesis that says underlying cash generation is deteriorating.
(iii) That the single-fee migration is float-neutral, from the filing language alone. (iv) That the
permanent recurring cost is bounded by the interest yield and is ~$30m a year, not a 400bp margin
event. (v) The 5 November expectation and the corrected reading rule.

**Cannot.** (i) **Separate a longer-dated book from pre-payment cancellations** — the balance sheet
is blind to bookings that fail before any cash moves, and `docs/rnpl-short-audit/04` reached the
same wall. The float loss in §4C therefore carries a 7.5x range. (ii) **Pin the customer-funds
yield** — not disclosed; term C scales one-for-one with it. (iii) **Identify 4Q25 or 2Q26
individually** — both are inside the noise band. (iv) **Attribute the funds-payable shortfall**;
funds payable carries an ±8.7pt annual FX swing plus payout-cadence and Pay-Less-Upfront mix, so
its $420m contribution to the central float loss is a hypothesis with the right sign, not a
measurement. (v) **Anything about the Street's FCF estimates** — that is object 3.

**Limits on the inputs.** `02_kpi_panel_quarterly.csv` FY2021 CFO/FCF does not tie to the 10-K
reconciliation: the panel gives FY21 FCF $2,288m against $2,164m in `abnb_fcf_bridge.csv`, which
does tie; the gap is $124m and sits almost entirely in 1Q21 ($112m). From 1Q23 onward the two agree to
$0.0m and every RNPL-era quarter ties exactly, so nothing in §§3–6 is affected. The 2021–2022 rows
of the panel are context only. `data/raw/letters/` does not exist on this checkout (gitignored);
letter language is quoted through the verbatim `quote` fields of the D-ledger and the guidance
ledger, both of which carry the source file path.

---

## 9. Next evidence

1. **IR ask (reinforces `04` item 5.1):** the unbilled balance behind the 10-K hedge disclosure —
   *"unbilled amounts for confirmed bookings under the terms of our payment programs (Pay Less
   Upfront and Reserve Now, Pay Later)"* (10-K p.50). That single number separates a longer-dated
   book from pre-payment cancellations and collapses the 7.5x range in §4C.
2. **Ask for the yield or the average customer-fund balance.** Either one turns §4C from assumed
   to derived.
3. **3Q26 10-Q, 5 November:** unearned fees stock, the cash-flow "Unearned fees" line, interest
   income, and whether the FCF-reconciliation paragraph changes again.
4. **Object 3 (Street perception)** decides whether any of this is priced. If FY27 FCF consensus
   has not moved while FY27 revenue consensus has risen, the mispricing is the *timing* of FCF per
   share, not its level — and this object says the level effect is only ~$106m.

---

## 10. Files

Written by `analysis/src/rnpl_short_audit/qog_cash_reality.py` into `data/processed/rnpl_short_audit/`:

| File | Contents |
|---|---|
| `qog_cash_reality_quarterly.csv` | the full quarterly panel 1Q21–2Q26: revenue, adj. EBITDA, SBC, CFO, capex, FCF, Δ unearned fees, FCF ex-float, SBC-adjusted variants, interest income and the customer-funds share, implied yield, all conversion ratios, same-quarter y/y and trailing-four-quarter series, and the FCF cross-check against `abnb_fcf_bridge.csv` |
| `qog_cash_reality_annual.csv` | FY2021–FY2025 plus 1H2025 and 1H2026 memo rows |
| `qog_cash_reality_seasonality.csv` | FCF, FCF ex-float and Δ unearned fees by quarter number, 2022–23 against 2024–26 |
| `qog_cash_reality_transition.csv` | the unearned-fees shortfall against the pre-RNPL norm, the drag per quarter, FCF ex-RNPL, and FCF-minus-revenue growth quarterly and trailing |
| `qog_cash_reality_forward_drag.csv` | 3Q26–2Q27 shortfall and drag under bear/central/bull, with the y/y change in the drag |
| `qog_cash_reality_bridge_2027.csv` | the §4 bridge with terms A–F, low/high bounds and memo rows |
| `qog_cash_reality_exhibit.csv` | the §2 exhibit, 1Q24–2Q26 |
| `qog_cash_reality_3q26_test.csv` | 3Q26 FCF and margin across guide low/mid/high × bull/central/bear × two ex-float bases |
| `qog_cash_reality_filing_facts.csv` | twelve filing facts with verbatim quote, location and evidence label |
| `qog_cash_reality_uf_reconciliation.csv` | the unearned-fees balance move against the cash-flow-statement line, five published periods |
