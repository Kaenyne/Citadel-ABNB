# RNPL quality-of-growth study: inflated KPIs, momentum, and the cash that actually arrives

- **Date:** 2026-09-11 (late evening). **Author:** Theo Machado, compiled with Claude Code, from two Opus build agents (05a cash-reality object, 05b momentum-reversal object) on top of the four-agent audit (00–04). Spec: `docs/superpowers/specs/2026-09-11-rnpl-quality-of-growth-study-design.md`.
- **Status:** objects 1, 2 and 4 built from filings and the repo; object 3 (Street perception) and the blanks in object 5 (return path) wait on the Bloomberg extraction workbook `data/raw/bloomberg/requests/2026-09-11_rnpl_qog_extraction.xlsx`.
- **Nothing existing was modified.** All files uncommitted.

## 1. Bottom line

1. **The top line is timing-inflated; the cash line is timing-misread in both directions; the durable cash cost is small.** RNPL's four mechanisms (uplift, pull-forward, deferral, propensity) inflate Nights and Seats Booked and GBV on a dated schedule that laps from 3Q26 to 1Q27 (notes 01, 02). On the cash side, stripping the unearned-fees float out of FCF shows conversion *improving*: 1H26 FCF ex-float +24.4% on revenue +17.1%, margin 29.7% vs 28.0%. The headline 47% vs 51% FCF-margin gap is entirely the float shift (note 05a).
2. **The RNPL transition drag was −$469M cumulative and is over.** 3Q25 −$30M, 4Q25 −$75M, 1Q26 −$340M, 2Q26 −$24M against pre-RNPL seasonal norms (noise sd $39M; only 1Q26 is individually identified). From 3Q26 the timing flips to a y/y tailwind on FCF: Q3 is the collection quarter and RNPL adds about $160M to 3Q26 FCF. Expected 3Q26 FCF $1,554M to $1,762M, margin 33.1% to 36.9%, against $1,349M and 32.9% a year ago.
3. **The permanent RNPL cost in 2027 is about $106M, 0.7 points of margin** (bear −$133M, bull −$51M): residual transition −$65M (derived), interest on float never collected −$29M (range −$11M to −$98M; the customer-funds yield is not disclosed, so the blended 3.6% is assumed), processing cost of a one-point higher cancellation rate −$11M (derived from the FY25 $1,666M merchant-fee line, 1.82% of GBV), single-fee working capital $0 (measured: 10-K Note 2 puts the host fee in unearned fees at receipt under both structures). Not a margin event.
4. **Momentum is at its peak and the reaction to deceleration is real but sits in the gap.** ABNB's 3/6/12-month price momentum is +36%, +36% and +47%, rank 1 of 17 against benchmarks and peers on all three; the 7 August +17.4% print has not faded; short interest 2.2% of float. Across 11 prints where nights decelerated, day-one excess return vs QQQ averaged −4.1% and was negative in 10 (9 of 9 since 2023); entered at the next open, the same prints were up 10 of 11. After prints where nights decelerated while revenue beat (10 cases), 20-day drift averaged −3.0% (70% negative) and 60-day −4.2%; no drift cell is separable from noise (note 05b).
5. **Consequences for the trade.** The 5 November print will carry a nights deceleration (module 9.5%, band 8.8 to 10.3, against a 10.0 guide floor) *and* a strong FCF optic. The cash leg cannot be scored on 5 November; it moves to 1Q27, when the global lap, the pull-forward reversal and the FCF timing all point the same way. The momentum leg is a pre-print positioning question, not a post-print chase. The shape trade into the February 1Q27 framing (note 03) stands; the print trade needs a positioned entry and a defined loss on a +17% day.

## 2. The exhibit (object 2, `qog_cash_reality_exhibit.csv`)

Same-quarter year over year. Nights and GBV measured; FCF ex-float = CFO − Δunearned fees − capex, derived.

| Quarter | Nights | GBV | Revenue | Adj. EBITDA | FCF | FCF ex-float |
|---|---:|---:|---:|---:|---:|---:|
| 1Q25 | +7.9% | +7.0% | +6.1% | −1.7% | −6.7% | −25.3% |
| 2Q25 | +7.4% | +10.8% | +12.7% | +16.7% | −7.8% | −3.3% |
| 3Q25 | +8.8% | +13.9% | +9.7% | +4.7% | +25.6% | +17.1% |
| 4Q25 | +9.8% | +15.9% | +12.0% | +2.7% | +13.8% | +19.8% |
| 1Q26 | +9.2% | +19.2% | +17.9% | +24.5% | −4.3% | +5.9% |
| 2Q26 | +10.3% | +15.7% | +16.5% | +20.9% | +30.2% | +39.5% |

Trailing four quarters: FCF +12.9% vs revenue +13.6%. The unpaid RNPL book ($3.3 to 6.9bn of GBV, note 04) is seven times the FCF-relevant slice, because the rest is host money in funds payable, which Airbnb excludes from FCF by definition.

## 3. The 2027 cash bridge (`qog_cash_reality_bridge_2027.csv`, central 25% RNPL share of GBV)

| Step | $M | Status |
|---|---:|---|
| A. FCF if RNPL did not exist | 6,031 | derived |
| B. Residual transition (share still rising) | −65 | derived |
| C. Interest on float never collected ($956M float loss) | −29 (−11 to −98) | derived on an assumed yield |
| D. Processing cost, +1 point cancellation rate | −11 (0 to −22) | derived |
| E. Single-fee working capital | 0 | measured |
| F. FCF with RNPL | 5,925 | derived |

Filing facts, verbatim locations in note 05a: interest income FY23 $721M, FY24 $818M, FY25 $705M, 2Q26 $183M, "consists primarily of interest earned on our cash, cash equivalents, marketable securities, and amounts held on behalf of customers"; customer-funds share derived at $382M of $705M; merchant fees and chargebacks FY25 $1,666M, "as the merchant of record, we bear all payment processing costs for our bookings".

## 4. The reaction base rates (object 4, `qog_momentum_cells.csv`)

Benchmark QQQ, arithmetic excess; day one split into overnight gap and intraday; drift from the reaction close; reproduces the repo's executable-returns file to machine precision and the drift file exactly except 1Q26 (a Memorial Day NaN row in the older price file slips that print's clock by one session).

| Cell | n | Day-one excess (mean / median / % negative) | Executable from the open | 20-day drift |
|---|---:|---|---|---|
| All prints | 22 | −0.1 / −0.3 / 55% | +1.2 / +1.2 / 27% | −2.5 / −3.3 / 59% |
| Nights accelerating | 8 | +3.5 / +4.0 / 25% | −0.8 / −2.4 / 63% | −3.4 / −2.4 / 63% |
| Nights decelerating | 11 | −4.1 / −3.9 / 91% | +1.8 / +0.9 / 9% | −2.2 / −3.6 / 64% |
| Decelerating, 2023 on | 9 | −5.9 / −7.1 / 100% | +1.3 / +0.8 / 11% | −2.0 / −3.6 / 67% |
| Decelerating and revenue beat | 10 | −4.1 / −5.0 / 90% | +1.5 / +0.9 / 10% | −3.0 / −4.4 / 70% (60-day −4.2 / −4.2 / 70%) |

The two prints in the last cell that did not fall (4Q22, 4Q23) were the two where the guide, not the KPI, was the story. No p-value is quoted for any cell, per the red team's ruling on the guide family.

## 5. Tests, re-pointed

| Test | Date | Rule | Change from the spec |
|---|---|---|---|
| Wedge | 5 Nov | reported nights growth minus the external stays read narrows in 4Q26 guidance and inverts in 1Q27 guidance | unchanged |
| Cash, stock | 5 Nov | (3Q26 unearned fees y/y − 3Q26 GBV y/y) ≤ −18 supports; −12 to −18 in line; > −8 weakens. Central mark $1,762M (−3.2% y/y), no-RNPL mark $2,068M, bear $1,734M | unchanged |
| Cash, flow | **1Q27, not 5 Nov** | 3Q26 FCF at or above 32.9% margin is *expected* and is not evidence against the thesis; 3Q26 FCF below $1,500M with unearned fees below $1,700M is strong support, above $1,800M with unearned fees above $1,900M weakens. The FCF-conversion test proper is scored on the 1Q27 print against the no-RNPL bridge | **re-pointed** |
| Perception | ongoing | FY27 FCF consensus revisions vs FY27 revenue consensus revisions since 6 Aug 2026 | needs Bloomberg tab 02 |
| Momentum | 5 Nov and Feb | a print or guide carrying a KPI deceleration while revenue estimates still rise; prior from the "decelerating and revenue beat" cell | unchanged; entry must be pre-print |

## 6. The return path (object 5, `qog_momentum_return_path.csv`), what is filled and what waits

| Row | Item | Bear / base / bull | Status |
|---|---|---|---|
| A | Spot (4 Sep 2026) | 181.94 | measured |
| B | 4Q26 nights y/y | 6.58 / 7.61 / 8.35 | module, derived |
| C | 1Q27 nights y/y | 5.28 / 6.47 / 7.34 | module, derived |
| D | Step-down vs "low double digits" | −3.4 / −2.4 / −1.7 points | derived |
| E | Revenue step from D | blank | needs the signed ADR path (card v2 + FX estimator choice) |
| F | Multiple step = E × 0.48 turns, applied once | blank | follows E |
| G, H, I | Day-one gap / executable / drift priors | from the cell above | measured, weak |
| J | Peer read-across | blank | needs BKNG, EXPE prints (workbook tab 07) |
| K | Revision response | blank | needs BEst history (workbook tab 02) |
| L | 3-to-12-month expected return = F + H or I + K | blank | follows |
| M | Size | 1 to 2% notional, defined loss on a +17% day | judgement |
| N | Flip rules | section 5 | pre-registered |

## 7. What this can and cannot identify

Can: that the FCF gap is timing, its size by quarter, its sign flip in Q3; the order of magnitude of the permanent RNPL cash cost and its three sources; the reaction base rates by KPI state and the fact that the deceleration effect is untradable after the gap; ABNB's momentum rank today.

Cannot: the customer-funds yield (assumed); whether the Street's FCF estimates already carry the timing (Bloomberg tab 02); the revision response and the peer read-across (blanks above); any drift claim at conventional significance. The lap magnitude behind rows B and C is fitted on four North American observations on an unmerged branch.

## 8. Files

- `docs/rnpl-short-audit/05a_cash-reality-object.md`; `analysis/src/rnpl_short_audit/qog_cash_reality.py`; `data/processed/rnpl_short_audit/qog_cash_reality_*.csv` (quarterly, annual, seasonality, transition, forward drag, bridge 2027, exhibit, 3Q26 test, filing facts, unearned-fees reconciliation).
- `docs/rnpl-short-audit/05b_momentum-reversal-object.md`; `analysis/src/rnpl_short_audit/qog_momentum_reversal.py`; `data/processed/rnpl_short_audit/qog_momentum_*.csv` (print panel, reconciliation, cells, cell members, state today, since the 2Q26 print, Bloomberg spec, return path).
- Extraction workbook: `data/raw/bloomberg/requests/2026-09-11_rnpl_qog_extraction.xlsx` (builder `analysis/src/rnpl_short_audit/build_bloomberg_extraction_xlsx.py`).
- Team page: https://claude.ai/code/artifact/d2a50fd7-fd7d-42a9-a3fe-e542f4abd99d
