# Does the travel complex read through to Airbnb?

*Prepared 2026-09-07. Question: analysts get Booking's and Expedia's room nights, and Marriott's and Hilton's RevPAR, days before Airbnb prints. Do they trade ABNB on it, does it fill a hole in Airbnb's own disclosure, and do competitor or industry announcements move the stock outside earnings?*

*New code: `analysis/src/peer_readthrough/01_fetch.py` … `05_mechanism_and_tradeability.py`. New data: `data/processed/peer_readthrough/`. Figure: `analysis/figures/peer_readthrough_abnb.png`. Builds on the existing fundamentals study in `analysis/src/predictive/02_peer_*` (peer KPIs → ABNB KPIs), which this note does not repeat except where it answers the question.*

**Sample.** 17 US-listed travel companies, every earnings release Dec 2020 – Sep 2026, dated from SEC 8-K Item 2.02 filings (460 filings; the reaction day is the filing date when the EDGAR acceptance timestamp is before 16:00 UTC, i.e. a pre-market release, otherwise the next session). 204 distinct peer reaction days, 308 peer-day observations after dropping the days Airbnb itself reported. Abnormal return (AR) is the residual of a market model against QQQ, betas fitted on the 250 sessions ending six days before, so the estimation window never sees the event. Every |AR| test is run twice — raw, and divided by ABNB's own trailing 120-day AR volatility — because ABNB's idiosyncratic vol roughly halved between 2022 and 2026 and the raw numbers otherwise say the readthrough decayed when it did not.

**Benchmarks to hold on to.** ABNB's mean |AR| is **1.46%** on an ordinary day and **6.74%** on its own print day (n=19). Everything below sits between those two numbers, much closer to the first.

---

## 1. The premise is half right: Booking usually does *not* report before Airbnb

| | reports before ABNB | median lead, days | Q4 season |
|---|---|---|---|
| Hilton | **86%** of quarters | 8 | +5 |
| Marriott | 64% | 2 | 0 (same day) |
| Booking | 55% | 3 | **−8 (reports after)** |
| Expedia | **45%** | 0 | +5 |

Hilton is the only member of the group that reliably prints well ahead of Airbnb. Booking has reported *after* Airbnb in five of the last six Q4 seasons (2021Q4 through 2025Q4, −6 to −9 days), which is exactly the print where a full-year guide is at stake. Expedia is a coin flip and most often lands the same day or the day before, which leaves no time to reposition. So the "read the peers, then trade Airbnb" trade has a usable calendar window in maybe half of quarters, and the name with the most reliable lead time is the one that turns out to carry the least information (§3).

Source: `data/processed/predictive/02_peer_prints.csv`.

## 2. Airbnb does trade on peer prints — but only the two OTAs, and only modestly

| Event set | n | ABNB mean \|AR\| | vs ordinary day (vol-adj) | p | share of days \|AR\|>2% |
|---|---|---|---|---|---|
| Ordinary day (baseline) | 988 | 1.46% | 1.00 | — | 25% |
| **All 17 peers, every print** | 308 | 1.51% | 1.06 | 0.07 | 25% |
| Hotels only (MAR/HLT/H/WH/CHH) | 86 | 1.53% | 1.08 | 0.19 | 23% |
| **BKNG + EXPE only** | 32 | 1.95% | **1.37** | **0.009** | 41% |
| BKNG/EXPE when the OTA's own move >5% | 16 | 2.35% | **1.66** | **0.003** | 50% |
| Any peer whose own move was ≤5% | 179 | 1.46% | 1.01 | 0.46 | 23% |

Three things fall out.

**The travel complex as a whole is not an ABNB event.** Pooling all 17 names, a peer print day is statistically indistinguishable from a Tuesday (1.06×, p=0.07 and in the wrong direction to be interesting). Hotels, airlines and cruise lines contribute nothing: Marriott 1.00×, Hilton 0.86×, United 0.76×, Southwest 0.65×. Airbnb is quieter than usual on a Hilton print day.

**Only Booking and Expedia move it, and only when they themselves move.** On the 32 OTA print days ABNB's idiosyncratic move is 37% bigger than normal, and on the 16 where the OTA's own abnormal move cleared 5% it is 66% bigger, with half of those days seeing ABNB move more than 2% on its own account. When the OTA print is a non-event for the OTA (≤5%), it is a non-event for ABNB too (1.01×). The readthrough is entirely a large-surprise phenomenon.

**It has not faded.** Raw |AR| on OTA days fell from 2.35% (2021-23) to 1.64% (2024-26), which looks like decay — but so did ABNB's baseline vol. Volatility-standardised the ratio is 1.42× then 1.34×. The relationship is intact; the stock is just calmer.

## 3. Expedia is the readthrough. Booking is not.

This is the sharpest result in the study, and it is the opposite of how the pair is usually discussed.

| | n | corr(AR_peer, AR_ABNB) | jackknife range | bootstrap 95% CI | Spearman | slope | same-sign |
|---|---|---|---|---|---|---|---|
| **EXPE** | 14 | **0.81** | 0.75 – 0.84 | 0.57 – 0.92 | 0.83 | **0.18** | 64% |
| **BKNG** | 18 | **0.01** | −0.09 – 0.12 | −0.39 – 0.43 | −0.11 | 0.005 | 44% |

The Expedia relationship survives dropping any single day (the jackknife never leaves 0.75–0.84), and the raw pairs are close to monotone: EXPE −18.8% → ABNB −3.1%; −16.2% → −2.4%; −14.2% → −5.2%; +17.7% → +4.7%; +17.9% → +3.1%. The slope says ABNB picks up about **18 cents of every dollar Expedia moves** on its print — well below the 0.47 beta ABNB carries to Expedia on ordinary days, i.e. the market correctly treats most of an Expedia earnings move as Expedia-specific and only passes through the industry part.

Booking is noise on every measure: correlation indistinguishable from zero, a *negative* rank correlation, and same-sign agreement of 44%, worse than a coin flip. BKNG −9.3% → ABNB +1.9%; BKNG −10.0% → ABNB −1.3%; BKNG −5.7% → ABNB +1.7%; BKNG +7.1% → ABNB +2.3%.

**The apparent contradiction is the interesting part.** Booking print days *are* more volatile than normal for ABNB (1.36×, p=0.05, §2) while carrying no directional information. ABNB gets shaken on Booking's day and then goes wherever it was going. Reading direction off Booking's tape is worse than not trading it.

Section 8 tests why.

## 4. The readthrough is a trade, not a forecast — it does not predict Airbnb's own print

For every Airbnb print, sum ABNB's abnormal return over the peer prints in the preceding 30 days ("readthrough drift") and compare it to what Airbnb then did.

| Signal | Target | n | Pearson r | p | Spearman | same-sign |
|---|---|---|---|---|---|---|
| OTA drift | ABNB day-1 AR on its own print | 14 | 0.27 | 0.36 | 0.06 | 57% |
| OTA drift | ABNB revenue beat vs guide midpoint | 14 | **−0.39** | 0.17 | −0.45 | **29%** |
| All-peer drift | ABNB day-1 AR | 19 | 0.18 | 0.46 | 0.24 | 58% |
| All-peer drift | ABNB revenue beat | 19 | −0.26 | 0.28 | −0.31 | 42% |

Nothing here is significant, but the signs are worth noting: the pre-print drift is unrelated to Airbnb's own reaction (rank correlation 0.06 — pure noise) and if anything *negatively* related to the size of the revenue beat, agreeing in sign only 29% of the time. Whatever the market puts into ABNB on Expedia's print day, it is not a better estimate of Airbnb's quarter.

The fundamentals side of the existing study (`data/processed/predictive/02_peer_readthrough_loo.csv`) says the same thing. In levels the correlations look spectacular — EXPE room nights y/y vs ABNB nights y/y r=0.98, Marriott RevPAR r=0.91 — but that is one shared post-COVID normalisation curve, and it does not survive the forecasting test. On the 2023Q1+ sample, leave-one-out MAE for ABNB nights y/y:

- naive "same as last quarter": **1.5 pp** (BKNG-availability sample) / 3.0 pp (EXPE sample)
- BKNG room nights: 3.0 pp — **worse than naive**
- Hilton RevPAR: 1.2 pp, Marriott RevPAR: 1.2 pp, EXPE room nights: 0.8 pp — better standalone, but n=6–13
- adding any peer signal to an AR(1): ratios 0.7–1.5, i.e. usually no better

Airbnb's nights growth has been so stable in the modern regime (~8–10%) that "last quarter's number" is a hard baseline to beat, and no peer signal beats it reliably.

## 5. What peers disclose that Airbnb doesn't — and whether it helps

Airbnb reports nights, GBV, ADR, regional nights y/y and regional ADR y/y. The genuine gaps, from `data/processed/overnight/02_metric_coverage.csv`:

| Hole in ABNB's disclosure | Status | Nearest peer fill |
|---|---|---|
| **Supply / active listings** | reported 4Q21–4Q25, then dropped | Hotel **net unit growth** (MAR, HLT, WH, CHH — guided annually) |
| **Occupancy / utilisation** | never disclosed | Hotel **occupancy**, reported by region alongside ADR |
| Cross-border share of nights | stopped 1Q24 | BKNG regional room nights |
| Long-term-stay share | stopped 1Q24 | none |
| Quarterly nights guidance (numeric) | never — qualitative only | BKNG/EXPE next-quarter room-night commentary |

The conceptual fit is real: RevPAR decomposes into the occupancy and rate that Airbnb refuses to split, and hotel net unit growth is the only regularly-guided supply number in the industry. But §4 is the verdict — hotel RevPAR beats a naive nights forecast by a fraction of a point on 12–13 observations, and hotel prints move ABNB not at all. The hole is filled in theory and not in practice.

## 6. Non-earnings industry events: one real case, and a lot of macro

Of ABNB's 60 largest abnormal days since the IPO, **12 are its own print** and **12 more fall on some peer's print day** — but eight of those twelve are days whose only peer was a small cap (HGV, TNL, SABR, VAC, CHH) or a hotel that §2 and §3 show carries no signal, so the overlap is coincidence at a base rate of 204 peer days in 1,440 sessions. Four survive as genuinely peer-driven: 2023-11-03 (EXPE +17.7% → ABNB +4.7%), 2023-02-10 (EXPE −7.8% → ABNB −4.4%), 2022-05-03 (EXPE −14.2% → ABNB −5.2%) and 2022-04-13, the Delta Q1 read-across (+7.3%, the only airline day that ever mattered). All three OTA days are Expedia's, which is §3 again.

The largest genuinely competitor-and-industry-driven move is **3 Feb 2026, the AI-disintermediation scare**: ABNB −7.0%, BKNG −9.3%, EXPE −15.3%, triggered by a Citrini Research note arguing AI agents could assemble itineraries more cheaply than the platforms by Q4 2026. This is the one day in six years where a third-party industry thesis, not an earnings release, repriced the whole complex — and note that Airbnb fell *least*, which is itself the market's view on relative disintermediation risk. It is the event type worth monitoring, and the two Third Bridge AI pieces already in `research/` are the standing coverage.

Everything else in the unexplained tail is macro or single-stock: rates and oil (24 Jun 2026 +5.0% on the 10-year through 4.5% and WTI −3%; 6 Dec 2021 Omicron-is-milder; 8 Mar 2022 oil reversal; 22 Sep 2022 Fed dots), index events (5 Sep 2023 S&P 500 inclusion), and analyst actions (13 Dec 2024 Barclays double-downgrade to Underweight, $135→$100).

## 8. Why Expedia? Because Expedia's print is industry news and Booking's is Booking news

Three candidate explanations, tested in `05_mechanism_and_tradeability.py`.

**Rejected: "Expedia just moves more."** Expedia's own mean |AR| on its print is 10.2% against Booking's 4.0%, and a bigger signal is mechanically easier to detect. But matching on signal size makes the gap *wider*, not narrower:

| | cut | n | mean \|AR_peer\| | corr | slope | same-sign |
|---|---|---|---|---|---|---|
| EXPE | all prints | 14 | 10.2% | 0.81 | 0.181 | 64% |
| EXPE | \|AR\| > 5% | 9 | 14.1% | **0.82** | 0.182 | 78% |
| EXPE | \|AR\| > 8% | 7 | 16.0% | **0.88** | 0.180 | 86% |
| BKNG | all prints | 18 | 4.0% | 0.01 | 0.005 | 44% |
| BKNG | \|AR\| > 5% | 7 | 7.7% | **0.21** | 0.049 | 57% |

Expedia's slope is 0.18 in all three cuts — a stable structural transmission coefficient, not an artefact. Booking's seven large prints still produce almost nothing.

**Rejected: "Airbnb simply trades like Expedia."** On ordinary days ABNB's beta is **0.57 to Booking** and **0.47 to Expedia** — it co-moves *more* with Booking day to day. Whatever separates them is specific to the earnings-day information, not to general co-movement.

**Confirmed: Expedia's print repriced the whole travel complex; Booking's doesn't.** Measure every other travel name's abnormal return on each reporter's day:

| Reporter's day | own \|AR\| | ABNB | EXPE | MAR | HLT | TRIP | BKNG |
|---|---|---|---|---|---|---|---|
| **EXPE reports** | 10.2% | **0.81** | — | **0.83** | **0.78** | 0.41 | 0.54 |
| **BKNG reports** | 4.0% | 0.01 | 0.07 | 0.31 | 0.30 | 0.24 | — |
| MAR reports | 3.7% | 0.26 | 0.45 | — | 0.79 | −0.06 | 0.35 |
| HLT reports | 2.5% | 0.25 | 0.40 | **0.82** | — | 0.09 | 0.25 |

*(correlation of the other name's abnormal return with the reporter's, on the reporter's reaction days)*

This is the answer, and it is not about Airbnb at all. When Expedia prints, **Marriott (0.83), Airbnb (0.81) and Hilton (0.78) all move with it** — the market treats an Expedia result as a statement about travel demand and reprices everything. When Booking prints, nothing moves: Expedia 0.07, Airbnb 0.01, the hotels 0.30. A big Booking move is big for Booking-specific reasons — European margin, marketing efficiency, buyback capacity, its own AI/Connected Trip narrative — and the tape treats it that way.

Note the fourth row too: hotel prints are industry news *for hotels* (MAR↔HLT 0.79–0.82) but Airbnb sits outside that circle at 0.25. The market prices ABNB as a travel-demand marketplace, not as lodging supply. That is a cleaner statement of §2's null than §2 could make on its own.

**One caution about the mechanism.** It is a price channel, not a KPI channel. Regressing ABNB's abnormal return on the peer's *reported room nights* rather than its stock gives nothing (BKNG room nights y/y r=0.16 p=0.52; EXPE r=−0.44 p=0.12), and — the giveaway — the peer's own stock does not respond to its own room-nights number either (all |r| < 0.36, p > 0.20). Room nights are not what moves these stocks on the day; guidance, margin and tone are. So the popular story ("analysts read Expedia's room nights and mark Airbnb") is wrong in its specifics. What actually happens is that Airbnb follows Expedia's *price*, which is responding to the whole content of the release.

## 9. Is any of it tradeable?

Booking and Expedia release after the close, so Airbnb reacts the next session and opens with a gap. Splitting ABNB's reaction-day abnormal return into the overnight leg (prior close → open) and the intraday leg (open → close), both QQQ-adjusted:

| Cut | n | share of move in the gap | corr gap | corr intraday | slope intraday |
|---|---|---|---|---|---|
| EXPE, all | 14 | 39% | 0.69 (p=0.006) | 0.52 (p=0.06) | 0.097 |
| EXPE, \|AR\|>5% | 9 | 40% | 0.69 (p=0.04) | 0.54 (p=0.14) | 0.099 |
| BKNG, all | 18 | 44% | 0.55 (p=0.02) | −0.39 (p=0.11) | −0.151 |

**The good news: ~60% of Airbnb's response is still on the table after the open.** The market does not fully reprice ABNB in the pre-market, so this is not a signal that only exists in an inaccessible session.

**The bad news is the sample.** The naive rule — at the open, take ABNB in the direction of Expedia's move, exit at the close, 10bp round trip:

| | n | trades/yr | mean | sd | per-trade Sharpe | annualised Sharpe | bootstrap 95% CI | P(edge > 0) |
|---|---|---|---|---|---|---|---|---|
| EXPE, all | 14 | 3.3 | **+0.82%** | 2.14% | 0.38 | 0.69 | −0.20 to +1.97 | 0.94 |
| EXPE, \|AR\|>5% | 9 | 3.0 | **+1.33%** | 2.39% | 0.56 | 0.96 | −0.10 to +2.85 | 0.97 |

Positive, economically sensible, and **not statistically established**: t = 1.4–1.7, and the bootstrap interval includes zero in both cuts. Gross of everything it is ~+2.7% to +4.0% a year on full notional at three trades a year. There is no way to grow this sample except by waiting — Expedia prints four times a year.

**Honest verdict: not a standalone strategy; a real positioning and sizing input.**

1. **Usable now, no statistics required:** holding ABNB through an Expedia print is taking an unhedged 0.18-beta bet on Expedia's result. On the nine large-Expedia-move days, ABNB's mean absolute move was 2.79%. If you don't want that exposure, the Expedia calendar is a risk date, and Expedia often reports 0–1 days ahead of Airbnb (§1), so the two risks stack.
2. **Trading it is a marginal-edge overlay,** appropriate to size small on an existing position, not to run standalone. Requires Expedia's own abnormal move to clear ~5%, which happens roughly 1.5 times a year.
3. **Never trade Booking's direction into ABNB.** The same rule applied to Booking has a 17% hit rate and t = −3.2 — nominally a contrarian signal, but with n=18 and no mechanism behind it (§8 says Booking's move contains no industry information), the right conclusion is "no signal, and size down through the volatility."
4. **The natural expression is options, and we can't test it.** Buying ABNB vol into an Expedia print is the cleaner trade than a directional stake, but the Bloomberg options data in `data/raw/theo_onedrive` is pull-date anchored rather than point-in-time (`theo-onedrive-data`), so implied-vol behaviour around peer prints cannot be backtested with what we hold. Flagging as the open question rather than answering it.

## 10. What to do with this

1. **Watch Expedia, not Booking, and only when Expedia's own move is large.** The setup is: Expedia prints, its own abnormal move clears ~5%. Expect ABNB to travel ~18% of it in the same direction, 78% of the time; on those nine days ABNB's mean absolute move was 2.79%. Roughly 60% of that is still available after the open (§9). Size it as an overlay, not a strategy — 3 trades a year at +1.3% mean, with a bootstrap interval that includes zero.
2. **Do not read direction off Booking.** ABNB is more volatile on Booking's day with no directional content — the worst combination. Booking's print is Booking news: nothing else in the complex moves with it either (§8). Size down through it and trade nothing.
3. **Put Expedia's print on the calendar as an ABNB risk date,** whether or not you trade it. Holding ABNB through it is an unhedged 0.18-beta bet on Expedia's result, and Expedia often prints 0–1 days ahead of Airbnb (§1), so the two risks land in the same week.
4. **Do not carry the readthrough into the print.** It has no predictive relationship with Airbnb's own reaction and a mildly negative one with the revenue beat. Whatever the peers imply, Airbnb's own print resets it, and at 6.74% mean absolute move the print dwarfs everything here by a factor of four.
5. **Ignore the hotels for the stock; keep them for the model, carefully.** Marriott and Hilton prints have zero effect on ABNB. Their RevPAR is the only public proxy for the occupancy Airbnb won't give, and it marginally beats naive on a 12-quarter sample — treat that as a sanity check on the nights forecast, not an input. (`forecast-every-quarter-independently` still applies.)
6. **The 2026 calendar risk is the AI-agent narrative, not a competitor print.** One industry note took 7% out of the stock in a day with no company news attached. That is the event class to have a pre-formed view on before Q3 (5 Nov 2026).

---

### Caveats

- The Expedia result rests on 14 events. The jackknife and bootstrap are reassuring (CI 0.57–0.92) but this is not a large sample, and roughly half of it is the 2022-23 period when both stocks were far more volatile.
- 8-K Item 2.02 acceptance timestamps are the release-timing source, and they are **UTC**, not Eastern, despite EDGAR's field naming — Hilton's shifts 11:01 → 10:02 across the DST boundary, i.e. a fixed 06:01 local release. Every release in the sample is either pre-market (10-12 UTC) or post-close (20-21 UTC), so a 16:00 UTC cutoff separates them cleanly; it would misdate a mid-session release, of which there are none.
- The BKNG and EXPE event sets overlap on two days (2023-05-05 and 2023-11-03, when both reported into the same session). Those days appear in both per-name samples, so the two are not fully independent.
- §9's trading rule is evaluated on the same 14 events that motivated it. There is no out-of-sample period, which is the main reason the verdict there is "not established" rather than "works".
- Vacasa, Sonder and Despegar were dropped: no usable price history from Yahoo over the window.
- IHG, Trip.com, MakeMyTrip and Despegar file 6-K, not 8-K, so they are absent from the earnings-date set. Trip.com in particular is a plausible readthrough for Airbnb's APAC nights and is not tested here.
- Post-event drift (t+1…t+5) is reported in `02_peer_summary.csv` but is not stable at these sample sizes and no claim is made from it.

### Files

| Path | What it holds |
|---|---|
| `analysis/src/peer_readthrough/01_fetch.py` | prices (yfinance) + EDGAR 8-K Item 2.02 earnings dates |
| `analysis/src/peer_readthrough/02_event_study.py` | abnormal returns, per-peer tests, era-matched permutations |
| `analysis/src/peer_readthrough/03_informativeness.py` | BKNG-vs-EXPE robustness, pre-print drift, hotel asymmetry |
| `analysis/src/peer_readthrough/04_figure.py` | the two-panel figure |
| `analysis/src/peer_readthrough/05_mechanism_and_tradeability.py` | why Expedia (M1-M3), gap-vs-intraday and the trading rule (T1) |
| `data/processed/peer_readthrough/02_event_days.csv` | every peer reaction day with ABNB's move |
| `data/processed/peer_readthrough/02_peer_summary.csv` | the full test grid |
| `data/processed/peer_readthrough/03_ota_event_log.csv` | the readable BKNG/EXPE log, newest first |
| `data/processed/peer_readthrough/02_abnb_top_moves.csv` | ABNB's 60 largest abnormal days, tagged |
| `data/processed/peer_readthrough/05_m2_response_matrix.csv` | who moves on whose print day - the mechanism table |
| `data/processed/peer_readthrough/05_t1_gap_vs_intraday.csv` | overnight vs intraday split of every OTA event |
