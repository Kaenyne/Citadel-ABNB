# Overnight run, 6-7 September 2026 — read this first

Fifteen workstreams ran overnight, plus the 16-26 follow-up, repair and integration series. All finished. A separate red-team pass re-derived 98 of the most
consequential numbers against the primary sources and re-ran all 34 analysis scripts (all clean, all
exit 0). Full detail is in `research/notes/overnight/14_master-synthesis.md`.

## The headline

**The base-case 12-month target fell from $248 a share to $181, and $55 of that $67 is the exit multiple
— not the business.** The rest moved $12 in total (−$5 EBITDA, −$4 net cash — the old model never subtracted the
~$0.7bn a year of RSU tax withholding — and −$3 from the FY2026 share-count fix, which had
double-counted the 1H26 buyback). Football field: bear **$74**, base **$157**, bull **$228**.
*(Revised 7 Sep 2026, workstream 26: the FY2028E lens is now discounted one year at the cost of equity
so all six lenses sit at the same ~30 Sep 2027 target date. Base football-field mean $160.22 -> **$156.79**,
base high $217.51 -> **$196.92**, bear mean $75.95 -> **$74.18**, bull mean $232.68 -> **$228.18**. The
undiscounted FY2028E value is kept as a labelled sensitivity row on the Valuation sheet and in
`13_valuation_summary.csv`. The base EV/EBITDA FY2027E lens -- the single number most people will quote --
is unchanged at **$180.88**.)*

*Convention, decided 7 Sep 2026 (workstream 25, audit finding A12): every price in this run is a
**12-month forward target** on FY2027E exit metrics, adopted target date ~30 Sep 2027, and "upside"
means a **12-month expected price return** from the 4 Sep 2026 close of $181.94 — not a present
discounted fair value. **All six football-field lenses now sit at that date**: five are values as of end-FY2027 and the sixth
(FY2028E) is discounted back one year at the cost of equity. Leaving it undiscounted -- as the run did
until 7 Sep -- was worth $11.46 of the base mean and is retained as a labelled sensitivity. Per lens:
`data/processed/overnight/25_valuation_conventions.csv`; the reasoning: `model/assumptions.md`,
"Model conventions, decided 7 Sep 2026".*

Workstream 12 attacked the exit multiple three independent ways — a time series of ABNB's own multiple
against forward growth, a 19-name cross-section, and a fade DCF — and all three landed below the
18 / 22 / 25.5x the 5 Sep model assumed. The recommended set is **13.5 / 16.5 / 18.5x**. For context:
the highest live sell-side target on the tape ($220) implies 19.3x, and the average target ($178.96
across 46 analysts) implies 15.4x. **Nothing published anywhere supports 22x.**

So, honestly: at $181.94 the stock is roughly at our base-case 12-month target. If the pitch is a long, the upside has to
come from one of exactly three places, argued explicitly — FY27 revenue above ~$16.0bn (we model
$15.84bn), SBC falling below ~10% of revenue (it is 12.9%), or a separately named and separately sized
optionality bucket. It cannot come from the exit multiple. **Growth is the only fundamental that has ever
moved this multiple: +0.48 turns per point of forward revenue growth. Margin moves it zero.**

## What we now know predicts what

**Almost nothing, and that is a defensible answer rather than a failure.** Across the run we ran roughly
3,500 tests. What survives:

- **The dollar forecasts the FX part of ADR.** Mechanical, real-time, walk-forward error 0.44x a naive
  baseline. The only genuine forecast we own.
- **The guide plus its trailing cushion forecasts the revenue *level*** with a 1.1% mean error. Airbnb has
  beaten its own midpoint 19 times out of 19 and finished above the *top* of the range 15 of 19. Scope it
  carefully: the same guide-plus-cushion is the **worst** baseline for the revenue **surprise vs Street**
  (walk-forward RMSE 2.03 pp against 1.33 for a trailing-4-quarter mean, n 10, WS20 section 3).
- **New tonight, and the most useful thing in the run: revenue FX lags spot by one to two quarters.**
  Revenue is recognised at check-in, so the FX effect on the revenue line arrives late. That means the
  Q4 2026 FX contribution is already **84% determined today**, at about −0.4 percentage points, against
  about +3 points in Q3. **The Q4 revenue guide will step down roughly 3 points on arithmetic alone, with
  no change in demand.** Have that bridge built before 5 November, not after. *(Built 7 Sep 2026, workstream 29:
  `research/notes/overnight/29_q4-fy27-bridge.md`; re-run `py -3.13 analysis/src/overnight/29_q4_fy27_bridge.py` weekly,
  it re-pulls FRED. Margin: workstream 30 `30_margin-walk.md` (quarterly walk and EPS proxy) and workstream 31
  `31_margin-model.md` (cost lines derived from the drivers, tested against history and against 194 management statements).)*
- **No reaction result survives once the return starts at the first executable price.** The
  nights-versus-Street-nights to 20-day drift looked like the run's one out-of-sample reaction result, but
  its 20-day window began at the **pre-release close** -- a price nobody can transact on the released
  numbers. Entering at the next session's open, LOO R-squared goes +0.156 to **-0.016** and the expanding
  walk-forward goes 0.958x to **1.076x** a zero baseline (WS20, `20_task_summary.csv`,
  `20_convention_restatement.csv`). Nothing predicts the day-one move either -- and 73% of the historical
  day-1 "signal" is the overnight gap, so only 3.2 points of the 6.8-point mean absolute day-1 move was
  ever capturable.

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
| Q4 guide | midpoint implying **+11-13%** — the Street is at $3,200m = +15.2% (a live "guide below Street" setup; 9/9 negative at 20 days, **mean -4.2% on an executable next-open entry**, base-rate p **0.038** on n 23) |
| FY26 guide | revenue raised to high teens; margin floor replaced by "approximately 36%+" |

**Frozen, pre-registered surprise forecast (WS20, `data/processed/overnight/20_frozen_q3_2026.csv`,
spec `ABNB-WS20-v1`, frozen 6 Sep 2026 -- do not change the spec before 5 November).** Because nothing
beat the baselines in both evaluation windows, the *designated* forecast is the surviving baseline, not a
model: **revenue surprise vs Street +1.37%** (1-sd +0.46 to +2.29 pp) on a $4,740m Street bar, implying a
**$4,805m** print; **nights surprise vs Street +1.83%** (1-sd +0.62 to +3.03 pp) on a ~145m bar, implying
**~147.6m** nights. Sixteen feature rows are stored alongside so their prospective errors can be scored
against that baseline on 6 November; two (`pr_hotel_revpar_yoy_pit`, `eu_platform_yoy_lag1`) are marked
PENDING because MAR and HLT report in late October and Eurostat 2Q26 is not yet published.

**The single most informative line in the release is brand-and-performance marketing.** It ran +32% in
1H26. Above +28% for the year and the FY margin lands at the 35.5% floor; below +20% and the reinvestment
cycle is easing, which is worth more to the margin case than any AI datapoint.

**The specific risk:** if management does not quantify the Q4 FX assumption the way they quantified Q3's,
the Street reads a mechanical dollar lap as a demand break. All **nine** prints where the guide came in below Street
had a negative 20-day return, **and this one survives an executable next-open entry** -- mean **-4.21%**
(median -4.42%) rather than the -8.90% the pre-release-close convention showed, with a
**base-rate-adjusted p of 0.038** against ABNB's own **69.6%** rate of negative 20-day excess on n 23
(WS20, `20_convention_restatement.csv`; the earlier 0.057 used n 22, before 2026Q2's 20-day return
landed). Quote the base-rate p, never the 0.0020 coin-flip figure. Exploratory, n 9. The day-1 half of
the rule collapses entirely on an executable entry: only 3 of 9 negative, mean +0.91%. Base rate for the
day: the average absolute move is 7.1%, and the direction is a coin flip -- and **there is no
options-implied number to use instead**. The 5 Sep line "the market prices no event premium (0.002 pts)"
is **withdrawn** (audit A08, WS23): the old estimator recovered E x (1 - T_near/T_far), not E, and the
6 Nov 2026 weekly was not listed on 6 Sep, so the only quotable option price is the 20 Nov straddle at
13.38% of spot -- which contains 75 days of background vol, not an earnings move. Re-run
`analysis/src/abnb_options_ledger.py` in the week of 26-30 Oct 2026. Positioning gives no cushion — spot is already above the average price target,
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

**Also stop quoting:** the seven-city Inside Airbnb retention fall of 75.4% → 71.1% (that set is
dominated by Austin's permanent listing-count step; ex-Austin the six-city move is **75.5% → 73.4%** and
the new-listing share is exactly flat at 25.4%, WS21 / audit A04), the Paris 33% / Nashville 44% /
Chicago 40% "supply exit" numbers (all artefacts of partial scrapes), and any ABNB event-implied move.

**Three claims to stop making:** the 18/22/25.5x exit multiples; "zero of 233 alt-data features beat
AR(1)" (the finished file has 598 rows and 52 do — the correct statement is that none survives *both*
windows); and the whole take-rate bull case as currently worded — "half of listings on the single fee",
"RNPL added 3 points of nights" (it was three features together), the −0.8pt direct-booking hit (from a
paywalled article nobody read), and the discount-share series (mislabelled and confounded by a scrape
change).

**Biggest risks:** the multiple staying at or below 16.5x (~65%, and it is our own base case); the Q4
guide being misread as demand (~35%); FY27 nights disappointing on the three-feature lap (~30%); a
strong-dollar path costing 2.6 points of FY27 revenue (~25%). Regulation and AI are both real and both
second-order through 2028 -- regulation is a **0.86%** revenue drag at the 2028 median with a **4.0%**
tail (WS22 repaired the Monte Carlo's conditional dependencies on 6 Sep, audit A06: the centre is
unchanged, the tail is honestly fatter -- the 2030 95th percentile goes 6.4% of revenue to **6.7%**,
$28.71 to **$30.04** a share), and no European regulatory event has ever moved this stock.

## Where everything lives

- **Read first:** `research/notes/overnight/14_master-synthesis.md` (this, in full), then
  `15_red-team.md` (what was wrong and what to fix), then `13_driver-model-build.md` (the model).
- **The model:** `model/ABNB_driver_model.xlsx` -- 9 sheets, **2,353** live formulas, **216/216** outputs
  reconciling to a Python mirror and to a real Excel 16.0 full rebuild (**0 error cells in 5,553**, and
  **144 scenario-switch comparisons, 0 mismatches**; WS17 / WS26, both audit scripts exit 0). Rebuild with
  `py -3.13 analysis/src/overnight/13_driver_model.py`, then `17_recalc_dump.ps1` (base, and with
  `-ScenarioValue 1` / `3`), `17_excel_audit.py` and `17_scenario_switch.py` -- and check the **exit
  status**, not the log. Assumptions in `model/assumptions.md`, sections "Overnight run 6-7 Sep 2026" and
  "Model conventions, decided 7 Sep 2026"; build order and machine prerequisites in
  `docs/overnight/BUILD.md`.
- **Notes:** `research/notes/overnight/01_*` to `18_*` plus the 19-26 repair and integration series — **26 notes at 7 Sep**, covering the data
  census, the KPI panel and 194-row guidance ledger, management language, consensus at all 23 prints,
  macro transmission, consumer choice and pricing, margin levers, alt-data backtests, stock behaviour,
  the regional build, competition and overlays, and the valuation regime.
- **Scripts:** `analysis/src/overnight/` — **59 files at 7 Sep** (58 Python plus the `17_recalc_dump.ps1` Excel driver), each rebuilding its own outputs with `py -3.13`.
- **Data:** `data/processed/overnight/` — one CSV set per workstream (**202 files at 7 Sep**, including `05_fred_cache/` and the JSON outputs; recount rather than quote this). The ones to open first are `05_fx_schedule.csv`
  (refresh this weekly), `12_exit_multiple_recommendation.csv`, `13_valuation_summary.csv`,
  `15_cross_note_conflicts.csv` and `15_claim_checks.csv`.
- **Figures:** `analysis/figures/overnight/` — 24 PNGs.

**Read the labels before quoting a number.** Three carried over from the 7 Sep conventions pass (WS25,
audit finding A12): prices are 12-month targets, not present fair values; the share count runs off a
2Q26 diluted **weighted-average** anchor standing in for a period-end fully diluted count, and the EPS
line is an **earnings proxy on modelled shares**, not GAAP EPS; and the consensus series is spliced
across vendors and vintages (StreetAccount, LSEG, Zacks, Visible Alpha, S&P Global) that differ by
roughly 2% on at least one nights comparison — keep the vendor column attached. Where this run says a
nights consensus or an options implied-move preview could not be found, it means **not found in public
previews on 6 Sep 2026**, not that none exists.

**Four things to do before anything else:** (1) update `model/assumptions.md` to the new exit multiples
with the old grid kept as a labelled sensitivity; (2) start refreshing the FX schedule weekly — it is one
hour of setup and the highest value per hour in the run; (3) freeze the prediction card in section 7 of
the synthesis before 5 November and score all nine items on 6 November; (4) start the monthly Inside
Airbnb capture, because their CDN keeps about a year and every month missed is a month that can never be
recovered.
