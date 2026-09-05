# ABNB major stock moves since IPO, with causes

**Source:** Yahoo Finance daily closes (10 Dec 2020 – 4 Sep 2026); QQQ/BKNG/EXPE same-day moves for attribution; Airbnb shareholder letters and call transcripts; same-day coverage (CNBC, Motley Fool, Reuters, Skift, Seeking Alpha, Nasdaq.com).
**Date:** 2026-09-05
**Author:** Krishang (compiled with Claude Code)

**Files:** chart `analysis/figures/abnb_major_moves.png`; events with full KPI detail `data/processed/abnb_major_moves_events.csv`; prices `data/processed/abnb_daily_close.csv`; 1/5/20-session earnings reactions vs QQQ `data/processed/abnb_earnings_reactions.csv` (from Theo's dataset, section 2b).

**Method.** Every close-to-close move of 7% or more (41 days). Each is attributed by checking whether QQQ, Booking and Expedia moved the same day (macro or industry) or not (company-specific), then confirming the trigger in same-day press. Peer moves are in the CSV.

## 1. What the 41 moves say

| Driver | Count | Pattern |
|---|---|---|
| Macro / market | 20 | Almost all in 2021–22: rates, Fed meetings, CPI, Ukraine, oil, tariffs (Apr 2025). ABNB moves 1.5–3x the Nasdaq on these days because it was the most expensive travel name. |
| Earnings | 11 | The only source of large moves since 2023 apart from tariffs and one AI scare. Six of the eleven were negative despite revenue and EPS beats. |
| Company / other | 9 | Post-IPO initiations (Jan 2021), refugee-housing PR and analyst reiteration (Aug 2021), Delta read-across (Apr 2022), S&P 500 inclusion (Sep 2023). |
| Competitor / industry | 1 | 3 Feb 2026 AI-disintermediation scare after hotel chains signed booking deals with Google/Anthropic/ChatGPT. Booking −9%, Expedia −15%, ABNB −7%. |

- Since 2023 the stock has been an earnings-day stock. Twelve of the last fourteen big moves were prints or macro shocks that hit every travel name equally.
- Earnings reactions key off **nights guidance**, not the reported quarter. Q3'22, Q1'23, Q2'24 and Q2'25 all beat on revenue and EPS and fell 8–13% on nights or lead-time commentary. Q4'24 rose 14% on a nights beat even though the revenue guide missed.
- There is **no management-change move**. CFO (Jan 2024), CTO (Nov 2025), CBO (Sep 2026) announcements each moved the stock under 3%. Executive turnover is not a catalyst the market trades.
- Competitor prints matter only when they carry an industry read-through: Expedia's Q3'21 beat (same day as ABNB's) and Delta's Q1'22 bookings. Booking's own prints never moved ABNB 7%.

## 2. Earnings-day reactions for all 23 prints

Next-session close vs. prior close. Bold = 7% or more.

| Quarter | Reaction day | Move | What decided it |
|---|---|---|---|
| Q4'20 | 26 Feb 2021 | **+13.3%** | First print; revenue $859M beat by ~$110M; recovery narrative (nights −39%, GBV −31%, ADR +13%) |
| Q1'21 | 14 May 2021 | +4.0% | GBV $10.3B (+52%) vs $7.9B est; revenue $887M vs $714M |
| Q2'21 | 13 Aug 2021 | +1.1% (−4% AH) | Nights 83.1M vs 79.2M; revenue +299%; Delta-variant caution |
| Q3'21 | 5 Nov 2021 | **+13.0%** | Record: revenue $2.24B, net income $834M, adj EBITDA $1.1B (49%); Expedia +15.6% same day |
| Q4'21 | 16 Feb 2022 | +3.6% | Revenue $1.53B vs $1.46B; Q1 guide $1.41–1.48B vs $1.24B; summer nights +25% vs 2019 |
| Q1'22 | 4 May 2022 | **+7.7%** | First 100M-night quarter (102.1M, +59%); GBV $17.2B (+67%); first profitable Q1; Fed-day rally added ~3 pts |
| Q2'22 | 3 Aug 2022 | −1.1% | Revenue $2.10B (+58%); $2B buyback; nights 103.7M (+25%) |
| Q3'22 | 2 Nov 2022 | **−13.4%** | Beat (revenue $2.88B, 51% EBITDA margin) but Q4 nights guided to ~20% from 25%, ADR flat; Fed hiked same day |
| Q4'22 | 15 Feb 2023 | **+13.4%** | First profitable year (NI $1.9B, FCF $3.4B); Q1 guide $1.75–1.82B vs $1.68B; nights 88.2M slightly light |
| Q1'23 | 10 May 2023 | **−10.9%** | Revenue +20%, first GAAP-profitable Q1, but Q2 nights growth guided below revenue growth; tough comps |
| Q2'23 | 4 Aug 2023 | −0.5% (−6% AH) | EPS $0.98 vs $0.78 beat; nights 115.1M below est |
| Q3'23 | 2 Nov 2023 | −3.3% | Revenue beat on FX; Q4 guide below Street |
| Q4'23 | 14 Feb 2024 | −1.7% | EPS $0.76 vs $0.67; Q1 guide in line |
| Q1'24 | 9 May 2024 | −6.9% | EPS $0.41 vs $0.24 but Q2 guide $2.68–2.74B vs $2.74B; flat Q2 nights guide |
| Q2'24 | 7 Aug 2024 | **−13.4%** | EPS $0.86 vs $0.92; nights 125.1M (+9%); shorter lead times and slowing US demand; Q3 nights to moderate |
| Q3'24 | 8 Nov 2024 | **−8.7%** | EPS $2.13 vs $2.17; S&M +27.5%, product dev +25%; EBITDA margin −200 bp |
| Q4'24 | 14 Feb 2025 | **+14.4%** | Nights 111.0M (+12%) vs 108.7M; EPS $0.73 vs $0.58; Q1 revenue guide below Street but ignored. Best day on record |
| Q1'25 | 2 May 2025 | +1.0% (−5% AH) | In line ($2.27B, EPS $0.24); soft Q2 guide; US softness |
| Q2'25 | 7 Aug 2025 | **−8.0%** | Beat ($3.10B, EPS $1.03 vs $0.94; nights 134.4M +7%) but H2 nights to moderate and ~$200M Services/Experiences spend |
| Q3'25 | 7 Nov 2025 | +0.3% | EPS $2.21 vs $2.31 miss; Q4 guide 7–10%; RNPL ~70% adoption |
| Q4'25 | 13 Feb 2026 | +4.6% | GBV +16% fastest in two years; Q1 guide 14–16%; FY26 "at least low double digits" |
| Q1'26 | 8 May 2026 | +0.7% (−2% AH) | Revenue +18% beat; EPS $0.26 vs $0.30 on $70M CAMT charge; FY raised to low-to-mid teens |
| Q2'26 | 7 Aug 2026 | **+17.4%** | Beat on every KPI: nights 148.3M (+10%), GBV $27.2B (+16%), EPS $1.37 vs $1.26; FY26 raised to at least mid-teens, margin ≥35.5% |

## 2b. What happens after the print: the move fades or extends, it does not reverse

Source: Theo's guidance dataset (`theos-past-research/research/guidance/data/normalized/market_returns.csv`, Nasdaq closes vs QQQ), copied to `data/processed/abnb_earnings_reactions.csv`. Excess = ABNB minus QQQ over the same sessions. His 1-day figures match the table above exactly. The 20-session window for Q2'26 was not complete at his 3 Sep cutoff.

| Quarter | Day 1 | Day 1 excess | 5-session excess | 20-session excess |
|---|---|---|---|---|
| Q4'20 | +13.3% | +12.9% | +1.8% | -2.8% |
| Q1'21 | +4.0% | +1.8% | -2.6% | +2.5% |
| Q2'21 | +1.1% | +0.7% | -4.7% | +6.8% |
| Q3'21 | +13.0% | +12.9% | +9.3% | -2.8% |
| Q4'21 | +3.6% | +3.7% | -9.2% | -9.1% |
| Q1'22 | +7.7% | +4.3% | -14.2% | -15.5% |
| Q2'22 | -1.1% | -3.9% | -2.5% | +1.0% |
| Q3'22 | -13.4% | -10.0% | -7.3% | -13.0% |
| Q4'22 | +13.4% | +12.6% | +9.3% | -3.5% |
| Q1'23 | -10.9% | -12.0% | -18.8% | -16.7% |
| Q2'23 | -0.5% | 0.0% | -2.1% | -7.7% |
| Q3'23 | -3.3% | -5.1% | -6.0% | -3.2% |
| Q4'23 | -1.7% | -2.8% | -0.4% | +6.5% |
| Q1'24 | -6.9% | -7.1% | -10.6% | -12.2% |
| Q2'24 | -13.4% | -12.3% | -15.6% | -16.5% |
| Q3'24 | -8.7% | -8.8% | -7.7% | -9.6% |
| Q4'24 | +14.4% | +14.0% | +5.4% | -2.4% |
| Q1'25 | +1.0% | -0.5% | +0.5% | -3.7% |
| Q2'25 | -8.0% | -8.4% | -6.9% | -5.3% |
| Q3'25 | +0.3% | +0.6% | +1.1% | +0.9% |
| Q4'25 | +4.6% | +4.4% | +8.9% | +10.1% |
| Q1'26 | +0.7% | -1.6% | -8.4% | -6.4% |
| Q2'26 | +17.4% | +16.3% | +19.6% | +22.2% raw ABNB (3 Sep close vs 6 Aug; QQQ excess not yet in Theo's file) |

- **Every 7%+ up day gave it all back within 20 sessions.** Q4'20, Q3'21, Q1'22, Q4'22 and Q4'24 all had negative 20-session excess returns (-2% to -16%) after +8% to +14% day-one pops. Q2'26 is the first exception: +22% raw after 20 sessions (from `abnb_daily_close.csv`), with no fade.
- **Every 7%+ down day stayed down or extended.** Q3'22, Q1'23, Q2'24, Q3'24 and Q2'25 finished 20 sessions at -5% to -17% excess. Nothing bounced.
- **The average print is a drag.** Mean 20-session excess across 22 prints is -4.7% (median -3.6%), positive only 6 times, against a mean day-one excess of +0.5%. Twelve of the 23 prints were in the 2021 to 2024 period when the stock went sideways to down, so this is partly regime, but the asymmetry between pops and drops is consistent across years.
- **For the pitch:** if the recommendation is a long into the 5 Nov 2026 print, the historical base rate says an in-line print drifts down and a beat gets sold within a month. The Q4'25 print (+4.6% day one, +10% after 20 sessions) and Q2'26 (+17% day one, +22% after 20 sessions) are the only two cases of a sustained post-print rally, both from the current RNPL and hotels reacceleration. A short pitch should note the same: the 17% squeeze on 7 Aug did not fade within a week.

## 3. Non-earnings moves worth remembering for the pitch

| Date | Move | Cause | Why it matters |
|---|---|---|---|
| 11 Feb 2021 | ATH $216.84 | Post-IPO initiations and reopening trade | The stock has still not regained this level (5+ years) |
| 9 May – 16 Jun 2022 | −12.1%, −8.1%, −9.2%, −8.1% | Fed/CPI growth selloff | ABNB fell below $100 for the first time; the multiple, not the business, was repriced |
| 28 Dec 2022 | Low $82.49 | End of 2022 bear market | Trough-to-now +120% |
| 5 Sep 2023 | +7.2% | S&P 500 inclusion | Passive demand, no fundamentals |
| 3 Apr / 9 Apr 2025 | −7.2% / +14.8% | Tariffs and the 90-day pause | ABNB moved in line with Expedia and Booking |
| 3 Feb 2026 | −7.0% | AI-disintermediation scare (hotel chains sign Google/Anthropic/ChatGPT deals) | The only competitor/industry-driven 7% day; Booking and Expedia fell 2x as much, so the market sees ABNB as less exposed |

## 4. Implications

1. **The catalyst that moves ABNB is a nights print, in either direction.** Build the pitch's catalyst calendar around the 5 Nov 2026 Q3 print and the Feb 2027 Q4 print, and the specific number the Street will anchor on (nights growth vs the "low double digits" guide, and the RNPL lap).
2. **Beats do not protect the stock.** Six of the eleven 7%+ earnings moves were down days on beats. The tell was always forward nights, lead times, or spending. For a long, the risk is the Q3'26 margin-down-YoY guide and the RNPL lap; for a short, the risk is the 17% squeeze seen on 7 Aug 2026.
3. **Macro sensitivity has fallen.** In 2022 ABNB moved 1.5–3x the Nasdaq; in 2025–26 it moved in line with peers on tariff days and less than peers on the AI scare. Beta to rates is no longer the main risk.
4. **Management changes are not catalysts.** No exec announcement produced a 3% move.
