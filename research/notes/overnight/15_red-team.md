# 15. Red-team verification of overnight workstreams 01-12

What this is: an independent re-derivation of the most consequential numbers in notes 01-12 against
the primary sources — the shareholder letters in `data/raw/letters/`, the IR call transcripts, FRED,
SEC-filed peer releases, and the CSVs each note cites — plus a re-run of every script in
`analysis/src/overnight/`. Nothing in other people's notes or CSVs was edited. Every correction below
names the file and line it applies to.

Deliverables: `data/processed/overnight/15_claim_checks.csv` (98 rows),
`15_cross_note_conflicts.csv` (16 rows), `15_script_runs.csv`.

---

## Bottom line

**98 claims checked: 83 confirmed, 9 wrong, 2 unsupported, 4 unverifiable.** The run is in good shape.
The statistics are, with one exception, better disciplined than the team's standards require — note 03
runs a 948-test Benjamini-Hochberg grid and reports that nothing passes; note 12 reports the
Durbin-Watson failure in its own headline regression; note 09 reports that its own best rule has
stopped working. Almost every wrong number is an overstatement of a result that is directionally right,
not an invention.

**The four things that actually matter:**

1. **The alt-data "survivor" is a window choice, and the two notes that discuss it contradict each
   other.** WS08's headline new finding — funds held for clients (lag 1) forecasting next-quarter
   revenue at 0.59x AR(1) — is 1.85x AR(1) (i.e. much *worse* than doing nothing) on the longer
   walk-forward window in the same file, `08_backlog_tests.csv`. WS08 reports only the favourable
   window and calls it "a genuine expanding-window walk-forward". WS01 quotes only the unfavourable one
   and declares the backlog coincident. Neither framing is complete. This is CONF-07 and it is the
   single most important correction in the run.

2. **WS01's census read a half-finished WS08.** WS01 finished at 01:56; WS08 wrote its CSVs at 02:16.
   WS01's two headline alt-data statistics — "zero of 233 point-in-time cells beat AR(1)" and "2 of 21
   indexes beat AR(1)" — do not match the finished files (598 rows of which 52 beat AR(1); 42 index
   rows of which 17 beat AR(1)). The census's *conclusion* survives; its *counts* do not. Any pitch
   slide quoting "zero of 233" is quoting a partial file.

3. **The exit multiple is the whole pitch.** WS12 triangulates three independent methods and all three
   land below the driver model's assumed 18 / 22 / 25.5x. At WS12's 13.5 / 16.5 / 18.5x, a 25/50/25
   weighting is worth **$190 (+5%)**; at the model's multiples it is **$249 (+37%)**. Every price in
   both grids reproduces exactly from FY27 EBITDA, net cash and share count. Nearly all of the stated
   upside currently sits in an assumption that no live sell-side target and no method supports.

4. **Four workstreams give four different FY27 revenue growths (10.3 / 11.3 / 12.3 / 12.4%) and two
   give two different 3Q26 revenue expectations ($4,775m vs $4,815m).** These are not independent
   estimates that can be averaged — WS05's 10.3% and WS10's 12.4% share the same FX schedule and differ
   only on nights. Pick one and show the others as the range (CONF-01, CONF-04).

**Nine claims are wrong.** In descending order of how much they matter: WS01's two alt-data counts
(above); WS11 attributing a three-feature nights uplift entirely to Reserve Now Pay Later, then
subtracting 3pts from the FY27 nights path on that basis; WS06's discount-share series, which is both
mislabelled and confounded by a mid-series change in the scraped quote schema; WS04's "the only
positive out-of-sample R² among 97 tests" (there are nine); WS05's "+2.9pp" FX prediction, which its
own file puts at +2.2pp, weakening the out-of-sample validation the note leans on; WS05's "fastest
nights growth in two years" (4Q24 was faster, six quarters earlier); WS03's "the only one of 79
features" (three of 79); and WS02's "+3 to +5 pts" nights-guide beat, contradicted by the note's own
cited instance of +1.2.

**All 34 scripts belonging to workstreams 01-12 were re-run end to end with `py -3.13`. All 34 exited
0.** Only three outputs moved a byte, all because the script re-fetches live data
(`08_trends_weekly.csv` +3 bytes on a fresh Google pull; `10_regional_benchmarks.csv` -1 byte;
`10_xbrl_revenue_geography.csv` 259 → 255 rows on a fresh EDGAR pull — WS10's *derived* outputs are
byte-identical either way, so the regional shares are unaffected). Those three were restored to their
pre-run state so notes 01-12 stay consistent with the data they were written on. Details in
`15_script_runs.csv`. The layer is genuinely reproducible.

---

## Per-workstream findings

### 01 — Data census
Structurally sound and useful; the CSV row count (217) checks out and the five-survivor framing is the
right frame. But the workstream ran ahead of WS08 and its two alt-data counts are wrong (see bottom
line 2). Its FX slope (-0.59 per pt of broad USD, n 14) is a real row in `05_fx_fits.csv` but is not
the fit WS05 and WS08 use (-0.715, n 17) — one slope must win (CONF-06). Its instruction to apply the
regulatory drag to EMEA nights rather than global revenue is correct and should be kept, because WS11
supplies both forms and applying both double-counts (CONF-14).

### 02 — KPI panel and guidance ledger
The most reliably verified workstream in the run. Every cushion statistic reproduces to two decimals
(mean beat +2.541%, median +2.52%, last-8 mean +1.856%/median +1.79%, 15 of 19 above the top, none
below the bottom, range width 4.76% → 1.90%). The FY24 SBC (+30.8%) and FCF-premium (+3.99 / +2.58 pts)
checks are exact. One wrong row: the "+3 to +5 pts" nights bucket-guide beat is contradicted by the
note's own cited +1.2 for 1Q26.

### 03 — Management language and the stock
The best-disciplined statistics in the run and the one workstream whose headline is a negative it
refuses to walk back: 948 tests, zero surviving BH q<0.10, best q 0.119, all reproduced exactly. Every
credibility-scorecard figure matches (62.1% overall, 80.0 / 73.3 / 26.3 by horizon, 42.1% Chesky,
0 of 7 on pricing). One overstatement: three of 79 features, not one, turn the day-1 LOO R² positive —
though all three are long-term-target variants, so the theme survives. Worth noting for the synthesis:
the note dismisses "text sentiment" wholesale, but *analyst* Loughran-McDonald tone has a detrended
r of +0.49 (perm p 0.016), materially stronger than any management tone feature. It is still post-hoc,
so it changes nothing, but the blanket sentence overstates.

### 04 — Consensus reconstruction
Exemplary construction: 23 prints, 145 sourced quotes, 97 tests all in one file. Every reaction
statistic reproduces exactly, including the 20-day nights-vs-Street drift (R² 0.220, slope +1.544,
t 2.458, perm p 0.053, LOO +0.133) and the guide-below-Street sign test with both the coin-flip
(p 0.004) and the honest base-rate (p 0.078) framings. One wrong headline: LOO +0.13 is *not* the only
positive out-of-sample R² among 97 tests — nine of the 75 LOO-evaluated specs are positive, and the
largest is post-2022 EPS surprise at 20 days (+0.222). The correct, still-strong statement is that
every positive-LOO spec is at 20 days and none is at day 1. Separately, the Zacks Q4-26 revenue figure
($3,200m) implies +15.2% y/y against WS05's expected +11-13% guide — that is a live "guide below
Street" setup for 5 Nov and the synthesis should surface it.

### 05 — Macro outlook and transmission
The FX mechanics are the strongest work in the run and every input verifies against FRED independently
(EUR/USD y/y +11.11 / +2.56 / -1.56 for 1Q26/2Q26/3Q26 QTD; broad USD -6.72 / -2.54 / -0.39; airline
fares +25.55% y/y in July 2026). The FY27 FX schedule and the probability-weighted scenario arithmetic
reproduce exactly. Two errors, both in the bottom line. First, the lagged revenue-FX fit predicts
**+2.2pp** for 3Q26, not +2.9pp — the note's own `05_fx_schedule.csv` says 2.19. The argument (lagged
beats contemporaneous) survives, but the validation against the guided +3.0pp is 0.8pp light, not
0.1pp light, and the note should not claim a near-perfect out-of-sample hit. Second, 2Q26's +10.34% is
the fastest nights growth **since 4Q24 (+12.35%)**, six quarters earlier, not the fastest in two years;
this appears twice. Note also that the FY27 margin scenarios are anchored on 36.5% imported from the
pre-existing margin-drivers note, so WS05 is not independent corroboration of WS07's 36.6% (CONF-02).

### 06 — Consumer choice and willingness to pay
The bedroom-mix argument is the most valuable original insight in the run and it verifies cleanly
against the 2Q26 letter ("grew over 12%" vs nights 10%, "more than 1 billion" LTM bedroom nights;
1,000/560.0 = 1.786 bedrooms per night; $183.73/1.786 = $102.89). The hedonic coefficients all match
(+15.05% per bedroom, +9.50% for rating ≥4.9, +1.01% Superhost), and the "do not model a Superhost
premium" conclusion is right. Two problems. (1) **The discounting series should not go on a slide as
written.** "10.9% (Mar 2026) to 31.4% (Aug 2026)" are cross-city medians, not the "share of available
quotes" the sentence claims — the quote-weighted shares are 17.3% → 31.4%. More seriously, the jump is
confounded: the share of quotes carrying a taxes line runs 0.20% (May) → 0.58% (Jun) → 5.65% (Jul) →
6.54% (Aug), and NYC swings 41.5 → 25.3 → 43.5 across the same dumps. That is a scrape/schema change,
not a behavioural one. (2) The "about half of active listings on the single fee by 2Q26" figure is in
neither the 2Q26 letter nor the 2Q26 call; the disclosed facts are "over a quarter" at 1Q26 and
"begun migrating the remainder … entire supply base by year-end" at 2Q26 (CONF-11).

### 07 — Ops and margin levers
Every cost-per-night figure reproduces exactly from `07_cost_lines_per_night.csv`: revenue/night
$20.29 → $24.33, cash cost/night $13.49 → $15.93, S&M 85.2% of the increase, brand & performance
+32.4% in 1H26 against field ops +24.4% (and the FY25 reversal, field ops +43.3% vs brand +9.6%). The
AI-support quantification — ops cash cost per night $2.130 → $2.049, worth +0.39 margin points — is the
cleanest single number in the run and I reproduced it end to end. Every peer-benchmark cell matches.
The AI-cost argument also holds against the primary source: I pulled `PurchaseObligation` and
`LongTermPurchaseCommitmentAmount` from the XBRL company facts and they are $719M → **$1,749M** and
$672M → **$1,700M** between the FY24 and FY25 10-Ks. That is the load-bearing rebuttal to Chesky's
"AI will not affect the P&L" and it is verified. One caveat rather than an error: the $1.18 brand /
$0.90 field split of the +$2.44 is a residual — the GAAP field-ops per-night delta is +$1.06, so the
two components sit on different bases. The headline (85% is S&M) is unaffected.

### 08 — Alt-data index and backtests
The negatives are excellent and correctly reported: 468 evaluable walk-forward pairs, 29 beating naive,
7 by ≥20%, and Google Trends failing on every one of 162 full-window pairs — all reproduced by summing
the scoreboard. The composite-index ratios match to three decimals. The problem is the one positive.
The funds-held → next-quarter-revenue result is presented as "the one genuinely new survivor" on the
strength of a 0.60x naive / 0.59x AR(1) walk-forward ratio over 10 quarters; the same feature-target
pair on the longer window in the same file is 1.69x naive / 1.85x AR(1) with 57% sign accuracy over 14
quarters. The note does not mention this. The jackknife stability it reports (0.55-0.66) is *within*
the favourable window only. Also: `fx_contribution_to_adr_3q26 = +0.80pp` is offered as "the single
number I would put on a slide", but the EUR/USD fit on the same data gives -1.27pp for the same
quarter and has the higher in-sample r — the honest presentation is the range (CONF-05).

### 09 — Stock behaviour and alpha
Everything checked reproduces exactly: the 20-session drift (-3.75%, t -2.164, p 0.042, negative 15 of
23), the up-print asymmetry (-7.10% at 20d, -14.80% at 60d, negative 8 of 10), the regime break from
2023 (-2.32%, t -1.15, not significant), all three seasonal effects against QQQ (May -14.48% 0 of 6
p 0.0016; Feb +7.67% 6 of 6; Nov -5.05% 5 of 5) and against the OTA pair, the 7.07% mean absolute
day-1 move, and the zero option event premium. The note's own honesty about selecting the May effect
from 54 tests, and about its best rule having failed in both 2026 prints, is exactly right. No errors
found. Its cost of equity (10.5-11.5%) disagrees with WS12's 10.3% and WS09's is the better-supported
number (CONF-08).

### 10 — Regional and segment decomposition
The reconciliation is the evidence that makes this usable and it holds: maximum residual 1.06pp,
mean -0.4075pp over the last four quarters. The 2Q26 shares and contributions match exactly
(NA 29.3 / EMEA 39.6 / LatAm 14.8 / APAC 16.2; contributions 2.35/3.17/2.96/2.92 summing to 11.40pp,
with LatAm+APAC at 51.6% of growth on 31.0% of nights). The FY25 NA revenue share (42.4%) reproduces
from the XBRL splits. The most valuable finding — that the guided "approximately three percentage point
FX tailwind" is hedges plus check-in lag, not spot, because the revenue-weighted spot basket is only
+0.32% y/y in 3Q26 QTD — is corroborated independently by FRED. The FX pass-through regressions
(r 0.97-1.00 on n of 5-10) are accounting identities rather than discoveries and should be described
that way. No errors found; the disagreements with WS05 and WS02 are in the conflicts file.

### 11 — Competition, supply and overlays
The BKNG comparison verifies against the primary filing (Q2'26 total room nights 325m, +5%; alternative
accommodation room nights +4%), and the regulatory overlay and new-business scenarios all reproduce.
Two issues. (1) **The +3pts of Q1'26 nights growth is attributed to Reserve Now Pay Later alone.** The
1Q26 call says: "we estimate these *three features* delivered approximately 3 points of nights booked
growth and approximately 4 points of GBV growth in Q1" — RNPL, the cancellation-policy redesign and the
single-fee migration together. WS11 then subtracts 3pts from the FY27 nights path and uses it to defend
a +6% bear case, so the misattribution propagates into the model (CONF-12). (2) **The -0.8pt take-rate
risk from the 6-10% direct-link pilot is unverified.** The Skift page exists and is real ("Airbnb is
offering some hosts direct booking links that come with a reduced service fee", 30 Aug 2026) but the
body is paywalled; the 6-10% range could not be read. -0.8pts is larger than the entire single-fee
benefit and would be the largest downside driver in the model. Separately, the "62.5 / 62.7 / 62.6 /
62.7 nights per average active listing" is arithmetically right but rests on listing levels rounded to
the nearest million ("over 8 million", "over 9 million"), so the ±0.2 constancy sits inside the input
error — and it restates a company disclosure ("active listings grew relatively in-line with Nights and
Seats Booked", 4Q25 letter). Keep the conclusion, drop the decimals.

### 12 — Valuation multiple regime
Arithmetically the cleanest workstream: all six football-field prices reproduce exactly from FY27
EBITDA, net cash and share count, as do the 25/50/25 weightings ($190.5 vs $249.0), the value of one
turn ($8.6 / $10.3 / $11.8), the +190% LTM EBITDA / -61% multiple decomposition, every current
multiple in the peer file, and the 22-raises / 0-cuts / +12.61% median analyst tally. The 30-regression
grid reports its own Durbin-Watson problem and its own weaker change-specification — that is how it
should be done. Net cash ex float ($9,593M) is exact against XBRL at 30 Jun 2026
(6,821 + 5,248 − 2,476), as is the $12,224M of funds held for clients that it excludes. Three cosmetic
internal inconsistencies to fix: NTM EBITDA is 18.5x in the peer file and section 2 but 18.2x in the
For-the-model table; `12_peer_multiples.csv` carries net cash of $9,569M against the note's correct
$9,593M; and the 10-year yield is labelled 4 Sep but 4.77% is the 3 Sep DGS10 print.

---

## Corrections to apply

The synthesis workstream should apply these. Exact file, exact replacement.

| # | File | Where | Replace | With |
|---|---|---|---|---|
| 1 | `research/notes/overnight/01_data-census.md` | line 19 | "of the 233 point-in-time feature-target cells in `08_feature_tests_all.csv` (Trends 152, Eurostat 32, backlog 21, Inside Airbnb 18, components 10), **zero beat an AR(1) walk-forward**" | "of the 598 feature-target-window cells in `08_feature_tests_all.csv` (Trends 432, Eurostat 64, backlog 42, Inside Airbnb 36, components 24), only 52 beat an AR(1) walk-forward and 25 beat both AR(1) and naive — and every one of those either is the mechanical FX pair, is not knowable before the print, or survives on only one of the two evaluation windows" |
| 2 | `01_data-census.md` | line 123 | "2 of 21 (FX 0.42x, price 0.65x)" | "17 of 42 rows (FX→ADR-FX effect 0.42x is the only one that also beats naive by >20%; price index→ADR 0.68x)" |
| 3 | `01_data-census.md` | line 16 and line 137 | "17 of 21" for the nights-acceleration sign rule | keep, but add "(from `2026-09-06_predictive-study.md`; on tonight's `04_reaction_tests.csv` the same feature has R² 0.032 and LOO R² -0.18 — it is a base rate, not a model)" |
| 4 | `01_data-census.md` | For the model table | "FX effect on ADR per +1 pt USD broad y/y: -0.59" | "-0.715 (n 17, ex-2021 window, r -0.964) — the fit WS05 and WS08 both use; the -0.59 post-2022 n=14 fit is the alternative" |
| 5 | `research/notes/overnight/02_kpi-panel-and-guidance-ledger.md` | line 213 | "Nights bucket-guide beat \| +3 to +5" | "Nights bucket-guide beat \| +1 to +5 (4Q25 +4.8, 1Q26 +1.2)" |
| 6 | `research/notes/overnight/03_management-language-and-stock.md` | line 39 | "It is the only one of 79 features that turns a numbers-only day-1 model from LOO R² −2.31 into **+0.34**" | "It is one of only three of 79 features that turn a numbers-only day-1 model from LOO R² −2.31 into positive territory (+0.34, +0.29, +0.13) — and all three are long-term-target variants of the same construct. The −2.31 baseline is itself a badly overfit n=17 model, so treat the delta as descriptive" |
| 7 | `research/notes/overnight/04_consensus-and-reaction.md` | bottom line item 4 | "**LOO R² = +0.13** — the only positive out-of-sample R² among 97 tests" | "**LOO R² = +0.13** — one of nine positive out-of-sample R² values among the 75 LOO-evaluated specs, and the best of the full-sample ones. Every positive sits at 20 days; not one is at day 1" |
| 8 | `research/notes/overnight/05_macro-outlook-and-transmission.md` | line 15 | "the two-quarter-lagged fit predicts **+2.9 pp**" | "the two-quarter-lagged fit predicts **+2.2 pp** (`05_fx_schedule.csv`, 2026Q3) against the guided ~+3.0 pp — close, and far closer than the contemporaneous fit's -1.6 pp, but not exact" |
| 9 | `05_macro-outlook-and-transmission.md` | lines 21 and 135 | "the fastest nights growth in two years (+10.3%)" | "the fastest nights growth since 4Q24 (+10.3% against 4Q24's +12.3%)" |
| 10 | `research/notes/overnight/06_consumer-choice-and-willingness-to-pay.md` | line 39 | "the share of available quotes carrying a discount rose from **10.9% (Mar 2026) to 31.4% (Aug 2026)**, higher in **all 13 cities**" | "the quote-weighted share of quotes carrying a discount rose from **17.3% (Mar 2026, 10 cities) to 31.4% (Aug 2026, 13 cities)**, and the median city went 10.9% → 31.4%, higher in every city with an April and an August read. **Caveat:** the share of quotes carrying a taxes line item rose 0.20% (May) → 5.65% (Jul) → 6.54% (Aug) over the same dumps and New York swings 41.5 → 25.3 → 43.5, so part of the move is a change in the scraped quote schema. Not slide-ready without a matched-listing panel" |
| 11 | `06_consumer-choice-and-willingness-to-pay.md` | line 173, and bottom line item 4 | "**about half by 2Q26**" | "the remainder in migration at 2Q26 (share not disclosed; 'over a quarter of our active listings' was the last disclosed figure, 1Q26 call)" |
| 12 | `06_consumer-choice-and-willingness-to-pay.md` | lines 37 and 204 | "0.02% of quotes" (cleaning-fee line) | "0.006% of quotes" |
| 13 | `06_consumer-choice-and-willingness-to-pay.md` | For the model table | Take rate FY26 "13.2-13.3%, flat vs 2025" | "13.4%, flat vs FY25's actual 13.41% — 13.2-13.3% would be a 10-20bp decline, not flat" |
| 14 | `research/notes/overnight/11_competition-supply-and-overlays.md` | lines 279 and 317 | "+3 pts of nights growth in Q1'26 from Reserve Now Pay Later" | "+3 pts of nights growth and +4 pts of GBV growth in Q1'26 from **three features together** — RNPL, the redesigned cancellation policies and the single-fee migration (1Q26 call, verbatim). RNPL alone is an unknown fraction of that, so the FY27 nights haircut should be smaller than 3pts or explicitly labelled as the full three-feature lap" |
| 15 | `11_competition-supply-and-overlays.md` | lines 26 and 312 | "on ~50% of listings at Q2'26" | "on over a quarter of active listings at Q1'26 (disclosed) with the remainder in migration through 2H26; the ~50% figure is not in the Q2'26 letter or call" |
| 16 | `11_competition-supply-and-overlays.md` | line 26 and the take-rate-downside row | the 6-10% pilot and the ~-0.8pt take-rate impact | keep with the flag "**unverified — the Skift article is paywalled; the 6-10% range and the -0.8pt scaling have not been read from a primary source.** Do not put -0.8pts in the model until confirmed" |
| 17 | `research/notes/overnight/12_valuation-multiple-regime.md` | line 411 | "18.2x NTM EBITDA" | "18.5x NTM EBITDA (as in `12_peer_multiples.csv` and section 2)" |
| 18 | `data/processed/overnight/12_peer_multiples.csv` | ABNB row, `net_cash_musd` | 9,569 | 9,593 — the note's figure is the correct one (XBRL 30 Jun 2026: cash 6,821 + STI 5,248 − LT debt 2,476); the peer file uses total debt 2,496 |
| 19 | `12_valuation-multiple-regime.md` | For the model, cost of equity row | "10y 4.77% (FRED DGS10, 4 Sep 26)" | "10y 4.77% (FRED DGS10, **3 Sep 26** — the 4 Sep print was not published)" |
| 20 | `model/assumptions.md` | exit multiples | 18 / 22 / 25.5x | 13.5 / 16.5 / 18.5x per WS12, with the 18/22/25.5 grid retained as an explicit "if the market keeps paying 2026 multiples" sensitivity |

---

## Claims that should not appear in the pitch

1. **"Zero of 233 alt-data features beat an AR(1) baseline."** The finished file has 598 rows and 52
   beat AR(1). The defensible version is: *nothing in the alt-data layer beats AR(1) on both evaluation
   windows, and every apparent winner is either mechanical FX, not knowable before the print, or
   window-dependent.*
2. **"Funds held for clients forecasts next-quarter revenue at 0.6x a naive baseline."** True on one
   window, 1.85x AR(1) on the other, from the same file. If it is used at all, it must be used with
   both numbers.
3. **"Airbnb's discount share tripled from 11% to 31% between March and August 2026."** Mislabelled and
   confounded by a mid-series scrape change.
4. **"A -0.8pt take-rate hit from the direct-booking pilot."** Rests on a paywalled article that could
   not be read.
5. **"Reserve Now Pay Later added 3 points of nights growth."** It was three features, not one.
6. **"The only out-of-sample signal in 97 tests."** There are nine.
7. **"1H26 was the fastest nights growth in two years."** 4Q24 was faster.
8. **"The FX model predicted the +3pp guide out of sample."** It predicted +2.2pp against +3.0pp.
9. **"18 / 22 / 25.5x exit multiples."** No method and no live sell-side target supports them; the
   highest target on the tape ($220) implies 19.3x.
10. **"Nights per listing has been 62.5-62.7 for four years."** Say "flat within the rounding of the
    disclosures" — the inputs are ±0.5m listings.

## Licensed content (Third Bridge)

Checked all twelve notes for quotation from the five PDFs in `data/raw/licensed/third-bridge/`. Third
Bridge appears in notes 01, 06 and 11 only. **No excerpt exceeds ten words.** The longest are
"Airbnb and the rest have set a plateau" (8), "10 years best case" (4), "no commission from guest" (4)
and "15-16%" / "16-17%". Everything else is paraphrase, and WS11 labels its expert rows "(paraphrase)".
Nothing needs redacting.

## Method and what I did not check

- Verification used `py -3.13` against the CSVs each note cites, the 8-K Ex. 99.1 letters, the IR call
  transcripts (2026-Q1 JSON and 2026-Q2 text), FRED keyless CSV (DEXUSEU, DTWEXBGS, CUSR0000SETG01,
  CUSR0000SEHB, DGS10) pulled fresh on 6 Sep 2026, and the SEC-filed BKNG Q2 2026 release.
- The XBRL company facts were used directly for WS07's purchase obligations and WS12's net cash.
- **Not checked:** the Monte Carlo in WS07 (only its inputs), WS09's factor regressions (only its
  summary statistics), WS12's print-day decomposition, and WS05's full 1,408-pair macro grid (only the
  headline fits and the scenario arithmetic). Each is recorded as `unverifiable` in
  `15_claim_checks.csv` rather than confirmed.
- **Could not verify:** CoStar hotel ADR (subscription), the Skift host-fee pilot (paywall), and Zacks
  consensus (the notes store verbatim quotes and URLs, which is the right mitigation).
- The 08 note existed when this workstream started and was reviewed in full.

## For the model

This workstream supplies no new estimates. It supplies the arbitration between existing ones. These
are the values the driver model should use where two workstreams disagree; the reasoning for each is in
`15_cross_note_conflicts.csv`.

| Parameter | Use | Rather than | Source of the ruling |
|---|---|---|---|
| FY27 revenue growth, base | **+12.3%** | 10.3 / 11.3 / 12.4 | CONF-01 |
| FY27 revenue growth, low case | +10.3% (macro-adverse) | — | CONF-01 |
| FY27 Adjusted EBITDA margin, base | **36.6%** | 36.4-36.5 | CONF-02 |
| FY26 revenue, base | **$14.2bn**, labelled as an above-Street stance | — | CONF-03 |
| 3Q26 revenue on the 5 Nov card | **$4.78-4.82bn range**, not a point | a single number | CONF-04 |
| 3Q26 ADR FX contribution | **-1.3 to +0.8pp**, centred near zero | +0.80pp | CONF-05 |
| FX-to-ADR slope, broad USD | **-0.715pp per pt** (n 17) | -0.59 | CONF-06 |
| Alt-data features in the forecast | **none** | funds-held as a validated forecaster | CONF-07 |
| Cost of equity / WACC | **10.5%**, band 10.0-11.5% | 10.3% | CONF-08 |
| Mean sell-side target | **$178.96** (46 analysts) | 179.55 / 179.88 | CONF-09 |
| FY26 and FY27 take rate, base | **13.4% flat** | 13.2-13.3% | CONF-10 |
| Single-fee coverage at 2Q26 | **"over a quarter at 1Q26, complete by year-end"** | ~50% | CONF-11 |
| FY27 nights haircut for the RNPL lap | **smaller than 3pts, or labelled as the full three-feature lap** | -3pts for RNPL alone | CONF-12 |
| Exit multiple on FY27E EBITDA | **13.5 / 16.5 / 18.5x** | 18 / 22 / 25.5x | CONF-13 |
| Regulatory drag | **EMEA/NA nights drags inside the regional build only** | nights drag AND global revenue drag | CONF-14 |
| Nights-acceleration reaction rule | **base rate with its n** | a per-point coefficient | CONF-16 |

Net effect on the football field: applying CONF-13 alone moves the 25/50/25 weighted value from $249
(+37% vs $181.94) to **$190 (+5%)**. Applying CONF-01 and CONF-10 on top lowers FY27 revenue by roughly
0.5-1.5% against the most optimistic internal build. The pitch's upside case has to be argued on the
operating numbers or not at all.

## Files written

- `data/processed/overnight/15_claim_checks.csv` — 98 rows: workstream, claim, value claimed, value
  verified, source checked, verdict, note.
- `data/processed/overnight/15_cross_note_conflicts.csv` — 16 rows: id, parameter, the two
  workstreams, both values, the recommended value and why.
- `data/processed/overnight/15_script_runs.csv` — the 34 workstream-01-12 scripts in
  `analysis/src/overnight/` with status, exit code, wall time, whether outputs changed on the re-run,
  and stderr.
- `analysis/src/overnight/15_claim_checks.py` and `15_script_runs.py` — the generators, so a reviewer
  can regenerate all three CSVs.
