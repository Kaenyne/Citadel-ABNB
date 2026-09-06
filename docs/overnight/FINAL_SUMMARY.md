# Overnight run, 6-7 September 2026 — read this first

Fifteen workstreams ran overnight. All finished. A separate red-team pass re-derived 98 of the most
consequential numbers against the primary sources and re-ran all 34 analysis scripts (all clean, all
exit 0). Full detail is in `research/notes/overnight/14_master-synthesis.md`.

## The headline

**The base-case value fell from $248 a share to $184, and $55 of that $64 is the exit multiple — not the
business.** The operating case moved $9 in total (−$5 EBITDA, −$4 net cash, the latter an actual
correction: the old model never subtracted the ~$0.7bn a year of RSU tax withholding).

Workstream 12 attacked the exit multiple three independent ways — a time series of ABNB's own multiple
against forward growth, a 19-name cross-section, and a fade DCF — and all three landed below the
18 / 22 / 25.5x the 5 Sep model assumed. The recommended set is **13.5 / 16.5 / 18.5x**. For context:
the highest live sell-side target on the tape ($220) implies 19.3x, and the average target ($178.96
across 46 analysts) implies 15.4x. **Nothing published anywhere supports 22x.**

So, honestly: at $181.94 the stock is roughly at our base case. If the pitch is a long, the upside has to
come from one of exactly three places, argued explicitly — FY27 revenue above ~$16.0bn (we model
$15.84bn), SBC falling below ~10% of revenue (it is 12.9%), or a separately named and separately sized
optionality bucket. It cannot come from the exit multiple. **Growth is the only fundamental that has ever
moved this multiple: +0.48 turns per point of forward revenue growth. Margin moves it zero.**

## What we now know predicts what

**Almost nothing, and that is a defensible answer rather than a failure.** Across the run we ran roughly
3,500 tests. What survives:

- **The dollar forecasts the FX part of ADR.** Mechanical, real-time, walk-forward error 0.44x a naive
  baseline. The only genuine forecast we own.
- **The guide plus its trailing cushion forecasts revenue** with a 1.1% mean error. Airbnb has beaten its
  own midpoint 19 times out of 19 and finished above the *top* of the range 15 of 19.
- **New tonight, and the most useful thing in the run: revenue FX lags spot by one to two quarters.**
  Revenue is recognised at check-in, so the FX effect on the revenue line arrives late. That means the
  Q4 2026 FX contribution is already **84% determined today**, at about −0.4 percentage points, against
  about +3 points in Q3. **The Q4 revenue guide will step down roughly 3 points on arithmetic alone, with
  no change in demand.** Have that bridge built before 5 November, not after.
- **Nights versus the Street's nights number** predicts the 20-day drift (the only reaction result that
  survives out of sample). Nothing predicts the day-one move — three independent efforts now agree.

What does *not* work: Google Trends (432 tests, nothing), Eurostat platform nights, the Inside Airbnb
panel as currently built, macro (1,408 pairs, zero forecast nights — Michigan sentiment against nights is
r −0.05), management tone, peer read-across, short interest, and all three composite indexes we built.
**Nothing in the alt-data layer beats a simple AR(1) on both evaluation windows.**

## 5 November, pre-registered

Guide: revenue $4,690-4,770m (+15-17%), low-double-digit nights, margin down slightly from 50.1%.
Street: $4,740m.

| | Our number |
|---|---|
| Nights | **+10.2%** (147.2m) |
| ADR | **+3.8%**, FX contribution −1.3 to +0.8pp (centred near zero) |
| Revenue | **$4,801m (+17.2%)**; the honest card range is **$4.78-4.82bn** |
| Adj. EBITDA margin | **49.0%** |
| Q4 guide | midpoint implying **+11-13%** — the Street is at $3,200m = +15.2% |
| FY26 guide | revenue raised to high teens; margin floor replaced by "approximately 36%+" |

**The single most informative line in the release is brand-and-performance marketing.** It ran +32% in
1H26. Above +28% for the year and the FY margin lands at the 35.5% floor; below +20% and the reinvestment
cycle is easing, which is worth more to the margin case than any AI datapoint.

**The specific risk:** if management does not quantify the Q4 FX assumption the way they quantified Q3's,
the Street reads a mechanical dollar lap as a demand break. All eight prints where the guide came in below
Street had a negative 20-day return. Base rate for the day: the average absolute move is 7.1%, and the
direction is a coin flip. Positioning gives no cushion — spot is already above the average price target,
46% of ratings are Hold or worse, short interest is at a three-year low, and there have been 22 target
raises and zero cuts since August with the stock still ahead of them.

## For the pitch

**The variant perception:** the market is arguing about whether the 2026 nights re-acceleration is real.
It is, and it is already priced — the stock went from 13.3x to 18.2x forward EBITDA and 84% of the +17.4%
on the Q2 print was multiple, not estimates. What is *not* priced is (1) that FY27 reported growth will
look worse than FY27 demand because of a dollar lap we can already date, and (2) that half of ADR growth
is a bigger unit, not a higher price — Airbnb disclosed bedroom nights for the first time in Q2 (+12%
against nights +10%), which puts it at ~$103 per bedroom-night against $172 for a US hotel room.

**Three claims we can defend:** the FX lap, dated and validated against management's own quantification;
Airbnb taking share back from Booking.com for the first time since 2022 (Booking's alternative-
accommodation nights grew +4% against our +10.3%, verified against their SEC filing); and that the
multiple is set by forward growth and nothing else.

**Three claims to stop making:** the 18/22/25.5x exit multiples; "zero of 233 alt-data features beat
AR(1)" (the finished file has 598 rows and 52 do — the correct statement is that none survives *both*
windows); and the whole take-rate bull case as currently worded — "half of listings on the single fee",
"RNPL added 3 points of nights" (it was three features together), the −0.8pt direct-booking hit (from a
paywalled article nobody read), and the discount-share series (mislabelled and confounded by a scrape
change).

**Biggest risks:** the multiple staying at or below 16.5x (~65%, and it is our own base case); the Q4
guide being misread as demand (~35%); FY27 nights disappointing on the three-feature lap (~30%); a
strong-dollar path costing 2.6 points of FY27 revenue (~25%). Regulation and AI are both real and both
second-order through 2028 — regulation is a 0.87% revenue drag at the 2028 median with a 4% tail, and no
European regulatory event has ever moved this stock.

## Where everything lives

- **Read first:** `research/notes/overnight/14_master-synthesis.md` (this, in full), then
  `15_red-team.md` (what was wrong and what to fix), then `13_driver-model-build.md` (the model).
- **The model:** `model/ABNB_driver_model.xlsx` — 9 sheets, 2,303 live formulas, 216 outputs reconciling
  to a Python mirror; rebuild with `py -3.13 analysis/src/overnight/13_driver_model.py`. Assumptions in
  `model/assumptions.md`, section "Overnight run 6-7 Sep 2026".
- **Notes:** `research/notes/overnight/01_*` to `13_*` plus `15_red-team.md` — 15 notes covering the data
  census, the KPI panel and 194-row guidance ledger, management language, consensus at all 23 prints,
  macro transmission, consumer choice and pricing, margin levers, alt-data backtests, stock behaviour,
  the regional build, competition and overlays, and the valuation regime.
- **Scripts:** `analysis/src/overnight/` — 39 files, each rebuilding its own outputs with `py -3.13`.
- **Data:** `data/processed/overnight/` — 153 CSVs. The ones to open first are `05_fx_schedule.csv`
  (refresh this weekly), `12_exit_multiple_recommendation.csv`, `13_valuation_summary.csv`,
  `15_cross_note_conflicts.csv` and `15_claim_checks.csv`.
- **Figures:** `analysis/figures/overnight/` — 24 PNGs.

**Four things to do before anything else:** (1) update `model/assumptions.md` to the new exit multiples
with the old grid kept as a labelled sensitivity; (2) start refreshing the FX schedule weekly — it is one
hour of setup and the highest value per hour in the run; (3) freeze the prediction card in section 7 of
the synthesis before 5 November and score all nine items on 6 November; (4) start the monthly Inside
Airbnb capture, because their CDN keeps about a year and every month missed is a month that can never be
recovered.
