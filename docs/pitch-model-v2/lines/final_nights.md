# Final line — NIGHTS (Nights and Seats Booked)

Rationale file for the first settled line of the pitch model v2, written per **DEC-0026** ("every settled
line gets `docs/pitch-model-v2/lines/final_<line>.md` explaining word by word why the base number stands,
the git data and model behind it, every alternative, and how the thesis catalysts enter that number").

Scope: **base scenario only**, per **DEC-0020** (Theo: build and discuss the base first; short and breaker
rows are deferred). Short and breaker values exist in the dossiers and are quoted here only where they are
needed to explain why something is *not* in the base.

Standing rule for everything below, **DEC-0016**: scenarios are mechanical consequences of stated
assumptions. No input on this line was chosen to match a price, a target, or the memo's downside.

Branch `theo/pitch-model-v2`, HEAD `c82b968`. Dossier commits: H0/D1/V1 at `e39d9e4`, D2/D3 at `e6d9832`.
Web fetches: zero. Every number below is in this repository, except the Bloomberg MODL aggregate, which is
licensed and quoted only as a dated aggregate.

---

## 1. The line at a glance

| period | base nights (m) | y/y | how the number is constructed | decision id |
|---|---:|---:|---|---|
| 1Q23 | 121.1 | — | printed, 10-Q filed 2023-05-09 | DEC-0003 |
| 2Q23 | 115.1 | — | printed, 10-Q 2023-08-03 | DEC-0003 |
| 3Q23 | 113.2 | — | printed, 10-Q 2023-11-01 | DEC-0003 |
| 4Q23 | 98.8 | — | printed, FY23 10-K 2024-02-16 | DEC-0003 |
| 1Q24 | 132.6 | +9.50% | printed, 10-Q 2024-05-08 | DEC-0003 |
| 2Q24 | 125.1 | +8.69% | printed, 10-Q 2024-08-06 | DEC-0003 |
| 3Q24 | 122.8 | +8.48% | printed, 10-Q 2024-11-07 | DEC-0003 |
| 4Q24 | 111.0 | +12.35% | printed, FY24 10-K 2025-02-13 | DEC-0003 |
| 1Q25 | 143.1 | +7.92% | printed | DEC-0003 |
| 2Q25 | 134.4 | +7.43% | printed | DEC-0003 |
| 3Q25 | 133.6 | +8.79% | printed | DEC-0003 |
| 4Q25 | 121.9 | +9.82% | printed | DEC-0003 |
| 1Q26 | 156.2 | +9.15% | printed | DEC-0003 |
| 2Q26 | 148.3 | +10.34% | printed — the naive carry-forward the 3Q26 forecast is scored against | DEC-0003 |
| **3Q26** | **146.3** | **+9.5%** | reviews stays index raw read **+10.041%**, less the index's own **+0.518pp** W2 walk-forward bias = **+9.523%**, × 133.6m | DEC-0004, DEC-0024 |
| **4Q26** | **131.8** | **+8.12%** | team reference **+8.90%** (PR #32), less a **0.78pt** ex-NA fee-and-cancellation lap (case B), × 121.9m | DEC-0019 |
| **1Q27** | **169.02** | **+8.21%** | bridge path: NA +2.31 (0.291 weight) + ex-NA +10.773 (0.709), lap −0.742 − 0.363, event +1.0 | DEC-0025 |
| **2Q27** | **157.10** | **+5.93%** | same, ex-NA +10.452, lap −0.742 − 0.907, World Cup lap −0.5 | DEC-0025 |
| **3Q27** | **155.96** | **+6.23%** | same, ex-NA +10.131, lap −0.742 − 0.907, no event | DEC-0025 |
| **4Q27** | **139.77** | **+6.05%** | same, ex-NA +9.810, lap −0.742 − 0.907, no event | DEC-0025 |
| **FY27** | **621.84** | **+6.64%** | sum of the four quarters ÷ FY26 sum **583.11m** | DEC-0025 |

The y/y column for 1Q24–2Q26 is computed in this file from the printed levels (Airbnb discloses the level,
not the growth rate, in the KPI box); every level is a filing number.

Two mechanical warnings about that table, both real and both sourced in §5:

1. The 2027 y/y figures are computed against the **bridge's own FY26**, which still carries 3Q26 at
   **146.813m**, not the adopted 146.3m (`06_revenue_path_3q26_4q27_v2b.csv`, row `3Q26,base,nights_mm`).
   3Q27's +6.23% is 155.958 ÷ 146.813. On the adopted 146.3m the same level is +6.60%, and FY27 is
   **+6.73%** rather than +6.64% (arithmetic done in this file on the dossiers' own levels; the FY26 sum
   becomes 582.62m). The FY27 *level* does not move, because the 2027 quarters are built from regional
   growth rates and not chained off the literal 3Q26 level (D3 §7 conflict 1). What moves is the
   denominator, and nobody has re-run the package.
2. The path is not monotone: 1Q27 (+8.21%) is **above** 4Q26 (+8.12%). That is the +1.0pt Middle East event
   term and the fact that the ex-NA RNPL lap is only 40% phased in 1Q27. `06_pass_line.csv` tests exactly
   this ("1Q27 nights growth within 2 points of the 4Q26 exit unless a named lap explains it", gap 0.09,
   pass).

Alternatives carried beside each decided number (all in §3–§5):

| period | base | shown beside it |
|---|---|---|
| 3Q26 | 146.3 (+9.5%) | raw index 147.0 (+10.0%) · W1-corrected 144.8 (+8.4%) · external stack 145.9 (+9.2%) · team baseline 146.8 (+9.9%) · Street 149.0 (+11.5%) |
| 4Q26 | 131.8 (+8.12%) | case A 132.7 (+8.86%) · β=0.5 carry 131.6 (+7.93%) · Street 134.0 (+9.93%) |
| FY27 | 621.84 (+6.64%) | lap-schedule 1Q27 167.1 / 2Q27 157.8 (D2) · RNPL global lap +6.42% (alt_rnpl) · lap-treatment flip +8.17% |

---

## 2. History: what the filings say and how the file was built

**What the number is.** "Nights and Seats Booked" is a disclosed Key Business Metric. It is not a derived
figure and there is no basis choice to make on it.

**Which files.** Five files in this repo carry it, and H0 checked them against each other cell by cell:

- `data/processed/abnb_driver_history_quarterly.csv` — the file D1 and D2 recompute their forecast levels
  from (3Q25 = 133.6m, 4Q25 = 121.9m are read from here).
- `data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv` — the superset panel (nights,
  GBV, ADR, take rate, cash-basis cost lines, SBC by function, D&A, diluted shares).
- `data/processed/airbnb_quarterly_kpis.csv` — the shareholder-letter KPI box.
- `data/processed/abnb_edgar_quarterly_kpis.csv` — raw XBRL facts with filed dates.
- `data/processed/abnb_quarterly_costlines.csv` — GAAP revenue and cost lines.

**The XBRL fetch.** `analysis/src/abnb_costlines_from_xbrl.py` pulls
`https://data.sec.gov/api/xbrl/companyfacts/CIK0001559720.json` and derives Q4 as FY − 9M. H0 re-ran it on
18 Sep 2026: exit 0, wall 0.4s, max absolute difference against the committed file **0.0**, all 26 quarters
(receipt `data/processed/pitch_model_v2/receipts/H0/receipt.json`). That receipt covers the **GAAP P&L
layer**, not nights — nights is not an XBRL tag on this filer. Nights is first public in the same-day 8-K
Ex. 99.1 shareholder letter KPI box and then restated in the 10-Q/10-K MD&A "Key Business Metrics" table.
H0 stamps every row with the 10-Q/10-K filed date rather than the letter date, which is 0–2 days
conservative (H0 §8 open choice 4); nothing on this line depends on that.

**The one basis choice that matters for nights: there is none.** DEC-0003's three documented basis choices
are all cost-side or share-side — G&A on `ga_cash_ex_lodging` (adding back the 4Q23 ≈ $931M lodging /
withholding / transactional-tax reserve), SBC at 4Q23/4Q25 taken at the panel's $290M/$411M rather than the
driver-history $270M/$400M, and diluted shares at 4Q23/4Q25 taken at 640.0m/614.0m rather than
653.0m/613.0m. **None of them touches nights.** H0 §4's first row and §6's third row record the test: across
1Q23–2Q26, nights, GBV, ADR, revenue, take rate, Adj. EBITDA and the four GAAP cost lines agree **exactly
(max abs diff 0.0)** across all five files, with exactly two named exceptions, SBC and diluted shares at
4Q23 and 4Q25. So the 14 printed nights values are not a reconciliation outcome; they are one number that
five files copy.

**What did not reproduce, and why it does not matter here.**
`analysis/src/margin_build/02_financial_panel/run.py` exits 1 in this clone with
`FileNotFoundError: data/raw/xbrl/ABNB_companyfacts.json` — the raw store is gitignored and absent
(receipt `receipt_panel_attempt.json`). That failure blocks a fresh re-derivation of the **cash-basis cost
lines, D&A and the two corrected SBC/share cells**. It does not touch nights, which is already exact across
five independent files.

**The identity.** Airbnb defines ADR as GBV ÷ nights and seats booked, so `nights × ADR ≡ GBV` is an
identity, not a fit. D6 reproduced it independently:
`data/processed/pitch_model_v2/receipts/D6/d6_history_identity.csv`, max |deviation| **0.2703%**, worst
quarter **4Q24** (17,552.43 implied vs 17,600 printed). That matches
`05_backtests/B1_TAKE_RATE_RECONCILIATION.md` §3's independently-stated **0.270%** to the third decimal.
The residue is pure disclosure rounding: GBV is disclosed to the nearest $0.1bn (±0.25%) and nights to the
nearest 0.1M, so the identity is only checkable to about **0.32%**. It holds to the rounding. This matters
for the forward line because D6's GBV is built as our nights × our ADR (DEC-0018), so every nights
disagreement with the Street lands in GBV undiluted: at 146.3m × $176.9 the 3Q26 GBV is ~$25.88bn against
the Street's $26.35bn (D1 §7).

**Grade.** H0 is **B** (DEC-0003 "grade B accepted").

---

## 3. 3Q26: why 146.3m, word by word

The committed line is **146.3m, +9.5%** (DEC-0004, restated as the built-together line in DEC-0024). The
number is the reviews stays index's raw reading **corrected for the index's own measured walk-forward
bias**. Every step of that sentence is below.

### 3.1 From review dumps to review counts

Inside Airbnb publishes per-market dumps of the full review log for each listing. The team holds **363
market-vintages across 123 markets**, with review dates from 2018 to **17 Aug 2026**
(`docs/q3nowcast/SYNTHESIS.md` §2 row E). The raw dumps are not on this machine — they live in Krish's
`abnb_ia_capture` store — so the reproduction starts at the committed counted layer:

- `data/processed/q3nowcast/E/market_vintage_daily.csv` — **697,888 rows**, 123 markets, 363 vintages
- `data/processed/q3nowcast/E/market_vintage_monthly.csv`
- `data/processed/q3nowcast/E/market_geo.csv`

The scripts that produced them, `E1_inventory_and_discover.py` → `E2_download_reviews.py` →
`E3_review_counts.py`, **were not re-run** (D1 §5). That is a real limit, stated in the dossier: a counting
error inside E3/E4 would survive the D1 reproduction untouched.

### 3.2 What a "stay" is

The index counts **reviews**, grouped by listing and by review month, and reads their year-over-year change
as a proxy for stays. A review is written **after check-out**, so a review is a completed stay and it is
dated at the **stay**, not at the booking. Regions are assigned in `E4_build_index.py`'s
`REGION_OF_COUNTRY` map and aggregated with Airbnb's own FY25 regional nights shares — NAM 28.3, EMEA 41.6,
LatAm 17.9, APAC 12.3 (`E4_build_index.py`, `FY25_NIGHTS_SHARE`).

`E4_build_index.py` builds four y/y constructions, all inside one dump vintage unless stated:
`yoy_all` (every review, the primary and the one used; explicitly flagged in the docstring as "upward biased
by survivorship"), `yoy_mature` (both sides 12m+ old listings), `yoy_cohort` (identical listing set both
sides), and `yoy_vmatch` (2026 dump over a ~12-month-earlier dump, which removes the wedge).

### 3.3 The survivorship correction

A dump holds only the listings that are alive on the dump date. Reviews written by listings that have since
been delisted are gone from the file. So the year-ago side of a within-vintage y/y is systematically
missing reviews, and the y/y reads high.

The size of this is **measured, not assumed**. `E4_build_index.py`'s `wedges()` compares the same market and
the same review month in two different dump vintages and writes `survivorship_wedge.csv`;
`E7_report.py` converts the ratio to an annual attrition rate. The finding
(`docs/q3nowcast/SYNTHESIS.md` §2 row E, verbatim): "**15 to 16% of a month's reviews vanish per year of
dump age; within-vintage y/y runs ~20 pp high but the wedge is stable (20.7 vs 20.4 pp), which is why the
backtest works**."

That last clause is the whole design. The index does not try to remove a 20-point bias; it relies on the
bias being *stable*, so that the OLS mapping from index to nights absorbs it as an intercept. Which is
exactly what WPK-A later attacked — see §3.5.

Two more nuisances, both handled in `E6_nowcast.py`'s docstring: **truncation** (the August dumps stop on
their scrape date, so August is a part month) and **posting lag** (a review is written after check-out, so
the last days before a dump are incomplete). Both are handled by a **day-matched window** that ends *k*
days before the dump and is compared with the same calendar window **364 days earlier** — 52 weeks, so the
day-of-week mix matches. *k* comes from the posting-completeness curve measured on markets holding both a
June 2026 and an August 2026 dump.

Coverage caveat on the record: 111 markets, 88% of the base, have both July and August; **NYC, LA, SF and
Tokyo are absent from the August row** (SYNTHESIS §2 row E). And: same-listing review volume is **−3% to
−7%** y/y — all growth in the index is coming from listings under a year old.

### 3.4 The raw index read: +10.041%

`E6_nowcast.py`'s `implied_nights()` does three things and writes
`data/processed/q3nowcast/E/q3_2026_nowcast.csv`. The governing row is
`(measure = yoy_all, weighting = w_reviews, region = GLOBAL)`:

| cell | value |
|---|---:|
| `partial_index_3q26_pct` (1 Jul to dump minus *k*, day-matched) | 26.3462 |
| `gap_mean_pp` (partial-to-full-quarter gap, measured on 2023–2025) | +0.0872 |
| `full_index_3q26_pct` | 26.4335 |
| `n_fit` (quarters in the OLS, 1Q23–2Q26) | 14 |
| `slope` (nights points per index point) | **0.322138** |
| `intercept` | 1.525819 |
| `r` | 0.861819 |
| `wf_rmse_pp` (the band is the out-of-sample error, not the in-sample residual) | 1.4751 |
| **`implied_nights_yoy`** | **10.041046** |
| `lo` / `hi` | 8.5641 / 11.5179 |

**+10.041% on the printed 3Q25 base of 133.6m is 147.01m — rounded, 147.0m, which is exactly the Street's
lowest estimate.** That is the index's own headline. It is not our number, and D1's opening sentence says
so in terms.

The critical structural fact, stated in D1 §3: the index is a **stay-date** series mapped onto a
**booking-date** KPI by an OLS slope of **0.32 nights-points per index-point (r 0.86, 14 quarters)**. The
counting is the easy part. **The forecast lives in that mapping**, and the mapping absorbs the average
booking-to-stay lag historically but cannot see a late-quarter shift in *when* people book — which is
precisely where RNPL cancellations and any September demand shock would act.

### 3.5 The walk-forward backtest, and what 0.837 / 0.683 / 0.757 mean

`E5_backtest.py` runs an expanding-window walk-forward on the note-08 protocol: at each quarter *t* the OLS
of nights y/y on the index is **refit on data strictly before *t*** and scored against three baselines refit
the same way (naive `y[t−1]`, prior year `y[t−4]`, AR(1)). An RMSE **ratio below 1.0 means the feature
helped**; the team's pre-registered survivor hurdle is **≤ 0.75**.

Two windows are run (`E5_backtest.py` lines 132–145):

- **W1** = window `2022Q1+`, walk-forward scoring from **1Q23** → **14 scored quarters, 1Q23–2Q26**.
- **W2** = window `2023Q1+`, walk-forward scoring from **1Q24** → **10 scored quarters, 1Q24–2Q26**.

Recomputed from `data/processed/q3nowcast/E/backtest_wf_paths.csv` for feature
`GLOBAL|yoy_all|w_reviews`, lag 0, target `nights_yoy`:

| window | n | index RMSE (pp) | naive RMSE (pp) | **ratio** | mean error (pred − actual) |
|---|---:|---:|---:|---:|---:|
| W1 (`2022Q1+`, 1Q23–2Q26) | 14 | 2.4081 | 2.8766 | **0.8371** | **+1.631798** |
| W2 (`2023Q1+`, 1Q24–2Q26) | 10 | 1.4751 | 2.1591 | **0.6832** | **+0.518452** |

So **0.683** means: over the ten scored quarters, the index's out-of-sample error was 68% of what you would
have got by assuming next quarter's nights growth equals last quarter's. **0.837** means: over fourteen
quarters it was 84%. Both beat naive. **Only W2 clears the 0.75 hurdle.**

**The re-vintaging, which is why neither number is clean.**
`05_backtests/WPK_reviews-index-2023-vintage.md` (build A, 14 Sep 2026) bought a second Inside Airbnb
vintage — the Mar–May 2023 dumps, 114 files, 4.88 GB — and re-read the training quarters from fresh data
instead of from a stale dump. Three pre-registered tests, one pass and two fails:

- **T1, wedge constancy — FAILS.** The within-vintage y/y for Mar 2022–Feb 2023 is **+90.4%** read inside
  the fresh 2023 dumps and **+80.5%** read inside the same markets' Aug/Sep 2025 dumps: a **−10.0pp** global
  gap and **−6.6 to −15.4pp in every region**, on n = 114 markets / 1,357 market-months, against a pass line
  of ±2.0pp global and ±3.0pp regional. The wedge is **not flat in the age of the review month**: the
  2025/2023 ratio is 0.63 at 1–3 months of age, 0.71 at 36 months, 0.74 at 60. A within-vintage y/y read
  years after the fact is *lower* than the same y/y read fresh, and the gap grows with the y/y itself.
- **T2, attrition curve — FAILS its band**, pooled 2025/2023 ratio **0.660** at 26–40 months of age
  (n = 114 markets, 1,246 pairs) against a 0.75–0.90 band. WPK's own reading: **the band was mis-derived.**
  The E table's ~15%/yr hazard compounds to 0.68 over the actual 28.9-month gap, and the measured 0.660
  annualises to 15.8%/yr — consistent with the table. The disagreement is with the band, not the curve.
- **T3, NYC Local Law 18 — PASSES** (attrition-corrected NYC review flow −65.8% inside a −40 to −70 band,
  10pp below the CRA −56.1% guest-nights benchmark).

`analysis/src/q3nowcast_v2/E/V6_backtest_substituted.py` then re-runs the W2 walk-forward with the
2023-vintage reads substituted for the training quarters. D1 reproduced all four variants **byte-identical**
on this machine, without the raw mirror, because
`data/processed/q3nowcast_v2/E/market_vintage_monthly.csv` already holds the 2023-vintage counted months:

| variant | ratio |
|---|---:|
| as-is (no substitution) | 0.683 |
| **honest, 103-market variant** | **0.757** |
| literal rule | 0.841 |
| fourth variant | 0.713 |

**The honest re-vintaged W2 is 0.757.** WPK's verdict, verbatim: "after the re-run no separately measured
statistic keeps the stays index at survivor grade on either window."

`05_backtests/SR_QUARTER_SUBMISSION_READINESS_v1.md` (15 Sep) is the governing instruction on how this may
be said: "**Do not present the old 0.68x result as a current two-window validated forecast.**" DEC-0004
adopts the wording: "the three-ratio sentence (0.68 W2 / 0.84 W1 / 0.76 re-vintaged; clears 0.75 on
neither)". Memo v3 still prints the bare "walk-forward RMSE 0.68x the naive" and **must be changed before
submission** (D1 §7 conflict 1). That is a live open item on this line.

The honest two-sided statement, which D1 §6 spells out and the memo must keep both halves of: the index
**does** beat naive on both windows (0.683 and 0.837 are both below 1.0); what it fails is the stricter
0.75 survivor hurdle — on W1 outright, and on W2 once re-vintaged.

### 3.6 The bias correction: 10.041 − 0.518 = 9.523 → 146.32m

The same walk-forward paths carry a **mean error**, prediction minus actual. The index **over-predicts**:

- W2 (10 quarters): **+0.518452pp**
- W1 (14 quarters): **+1.631798pp**

`data/processed/pitch_model_v2/receipts/D1/d1_recompute.py` does the arithmetic:

```
10.041046  (index raw read, q3_2026_nowcast.csv)
−  0.518452  (mean walk-forward error, W2, backtest_wf_paths.csv, n = 10)
=  9.522594  ×  133.6m  =  146.32m      →  committed 146.3m   (|Δ| = 0.02m)
```

and the counterfactual that has to be said out loud:

```
10.041046  −  1.631798  (W1 bias, n = 14)  =  8.409248  ×  133.6m  =  144.84m  →  144.8m
```

**The choice of the W2 bias over the W1 bias is worth 1.5m nights.** The case for W2: it is the window on
which the index is a survivor by the pre-registered hurdle, and it is the window whose *scored* sample
(1Q24–2Q26) does not include the 2023 quarters whose vintage is the thing WPK-A found wrong. The honest
counter, which the memo should pre-empt rather than be shown: the re-vintaged W2 ratio is 0.757, above the
hurdle, so "W2 is the surviving window" is no longer strictly true; and W2's own training quarters are the
stale-vintage ones (WPK-A: "the scored statistic still moves because the walk-forward trains on the
substituted quarter").

**No script in the repo emits 9.5 or 146.3.** D1 §2 lists the point as *inherited*: "the *choice* of +9.5%
as the point (no script in my packages emits 9.5 or 146.3 — it is a judgement selection that the recompute
now shows is exactly the W2 bias correction)". The only file that states in the record that 146.3m is a bias
correction is
`docs/pitch-forecasts/questions/risk-q3-nights-meets-guide/datasets/adopted_print_states_v2.json` (A09
rev 2, 17 Sep): `centre_source` = "team nowcast +9.5% (reviews index 9.5-10.0 **bias-corrected 9.52**;
external stack 9.2; module 9.49)"; `sd_source` = the fresh-vintage W2 RMSE range 1.634–1.816; adopted object
**N(9.5, 1.70)**; P(≥147.0m) **0.386**, P(≥147.8m) **0.260**.

### 3.7 Three independent routes land at 146.3

DEC-0004's phrase "three routes agree at 9.49–9.52" means:

| route | y/y | level | source |
|---|---:|---:|---|
| bias-corrected reviews index | 9.5226 | 146.32 | `q3_2026_nowcast.csv` + `backtest_wf_paths.csv` |
| unified RNPL cohort module, base | 9.49 | 146.3 | `data/processed/rnpl_short_audit/rnpl_nights_module.csv` row (base, 3Q26) |
| H1–H2 seasonal bridge, pattern only | 9.49 | 146.3 | `nights_baseline_reconciliation.csv` row "H1-H2 bridge, pattern only"; `h2_bridge_v3_rebased_lines.csv` column `pattern_only` = 9.4917 |

The module's 9.49 is built as the PR #32 reference 9.89 plus four RNPL terms: **M1 level lap +0.304**
(the partial US lap, net of the July 2026 booking-type expansion), **M2 pull-forward −0.113**,
**M3 cancellation deferral −0.019**, **M4 propensity drag −0.568** — total **−0.396**. The bridge's 9.49 is
the 2023–25 seasonal transition applied to 2026 H1 with no lap and no event overlay at all. Three
constructions with almost nothing in common arrive within 0.03pp of each other.

### 3.8 The external stack: 12 series, median +9.23%

`analysis/src/q3nowcast/G2_external_backtests.py` → `data/processed/q3nowcast/G/G_nowcast_3q26_observable.csv`.
Twelve rows target nights (`target = nights_m_yoy_pct`); their predictions for 3Q26 have **median +9.2324%**,
range **6.753 to 11.961**, which on the 133.6m base is **145.93m ≈ 145.9m**. The twelve:

NTTO I-94 overseas arrivals (qtd 1 month) on two windows; NTTO Western Europe arrivals; five Spanish INE
series (hotel nights foreign, FRONTUR tourists, hotel travellers, hotel nights, FRONTUR visitors); TSA
throughput on two windows; CPI lodging SA and NSA.

Each carries its own walk-forward ratio in the same file — best **0.743** (NTTO overseas, W2), worst
**0.996** (TSA). The best external feature on this KPI overall is **hotel RevPAR at 0.665 (W2) / 0.755
(W1)** (D1 §6). Two honest limits: every fit in that file is labelled "in-sample fit on full window", and
SYNTHESIS §2 row G says the stack is "in-sample, not independent". It is corroboration of the level, not a
second forecast.

### 3.9 Why the team baseline 146.8 was retired

146.8m / +9.89% is **PR #32's NA-lap model, base** (`nights_baseline_reconciliation.csv`, row
"PR #32 NA-lap model, base", `q3_yoy_pct` 9.89, `q3_nights_mm` 146.8). It is a bridge with two fitted
product parameters (**RNPL +2.40** and **fee+cancellation +2.29 points of NA nights**) that lap in
**North America only**, with ex-NA carried unchanged from WS10.

Three reasons it lost, all on the record:

1. **It has no walk-forward score at all.** `PREREG_ABNB-INT-v1.md` D-02: "The index is the only team-built
   series that beats naive out of sample… **The team baseline is a bridge, not a scored object.**" The
   harness carries no team method on `nights_m`.
2. **Its fitted parameters cannot be error-bounded.** They live on `origin/krish/nights-quarterly`, are
   fitted on four WS10 NA estimates, and D2 §5 records: "A fitting error there passes straight through my
   reproduction untouched."
3. **PREREG D-02 also forbids the compromise.** Option (c), "index point with the baseline band", is called
   not defensible by the pre-registration itself, because it mixes a point and a band from different
   objects.

Cost of the switch, from PREREG D-02's own consequence line: nights 146.3 vs 146.8, GBV $25,816M vs
$25,906M, **5 bp of take rate**.

### 3.10 Why the Street is at 149.0, and what it assumes

**DEC-0005** sets the 3Q26 Street nights bar at **149.0m**: the value in the **Bloomberg MODL screenshot of
12 Sep 2026, n = 28**, low 147.0 / mean 149.0 / high 151.0. On the 133.6m base that is **+11.53%**.

Memo v3 prints **148.9m (+11.45%)**. V1 traced it: 148.9 does not reproduce from the 12-Sep MODL capture's
own transcription (which records 149.0); it matches a **different, earlier** "Bloomberg FA" capture of
**4 Sep 2026**, a single displayed level rather than a 28-name mean, used throughout
`research/notes/reverse_dcf/`. DEC-0005 resolves it at 149.0 and notes `E_positioning_card.py` already says
149.0. The headline "below the Street" therefore moves from 2.6m to **2.7m**.

**What the Street's number assumes.** Memo v3: the bar "is management's guide carried forward one-for-one
after the 2Q26 beat (same sign as the guide in 12 of 13 guided prints)", and it implies acceleration "for
only the fourth time in 16 prints". The 3Q26 guide itself is a **bucket, not a range**: "low double digits"
on nights (2Q26 shareholder letter, 6 Aug 2026, via `02_guidance_ledger.csv`). The **≥10.0% → 147.0m**
mapping is **ours**, not the company's (`nights_baseline_reconciliation.csv`, last row: "'low double
digits' mapped to >=10; not a company range").

**One thing the memo may not say.** There is **no Street nights baseline inside the harness**: the L0
vintage register's 19 `nights` rows are all `role=at_print` historical with `vendor_not_recorded`
(PREREG INT-02). The 149.0m bar is a Bloomberg MODL aggregate, not a scoreable consensus object. Every
"versus consensus" claim on this line is a **memo claim, not a harness claim**. Separately, PREREG INT-02
records that the "+10.2% consensus" circulating in older nights notes is **our own frozen WS20 card,
mislabelled** — it is not consensus and is not used here.

### 3.11 What would have to be true for each alternative

**147.0m (+10.0%) — the raw index read.** True if the index's over-prediction is noise rather than bias. The
mean error is +0.52pp on ten quarters with a walk-forward RMSE of 1.475pp, so the standard error of that
mean is roughly 0.47pp: the bias is about one standard error from zero. It is a real statistical position
to say "don't correct a bias you can't distinguish from zero". The cost of taking it is that you hand a judge
the Street's own lowest estimate as your number, and you have to explain why you measured the error and then
ignored it. Note that 147.0m is also management's "low double digits" floor, so at this level the breaker
case, the guide floor and the bottom of the sell-side range coincide exactly.

**144.8m (+8.4%) — the W1 bias correction.** True if the fourteen-quarter window is the right sample for
estimating the index's error. It is the more conservative reading and it has more data. The argument against:
W1's sample is dominated by the 2023 quarters, which are exactly the quarters WPK-A showed are read from a
stale vintage with a non-constant wedge, so W1's +1.63pp bias is partly an artefact of the measurement
problem rather than an estimate of the index's forward error. The argument for it is that W2's 0.757
re-vintaged ratio means W2 is not clean either. This is the single most defensible way for someone to say
our 146.3m is too high — we should say it first.

**145.9m (+9.2%) — the external stack median.** True if the twelve knowable macro series are a better read
than one purpose-built index. Its strength is that each series is public, each has its own walk-forward
score, and the hotel RevPAR family beats naive on W2 at 0.665. Its weaknesses are stated in its own note:
the fits are in-sample on the full window, the series are not independent of one another (five of the twelve
are Spanish INE), and the median of twelve fits is not a forecast object with a distribution. It is 0.3pt
below our point, which is corroboration, not a rival.

**146.8m (+9.9%) — the team baseline.** True if you prefer a structural bridge with fitted product
parameters to a scored alt-data series. It is what the rest of the model was still running on when D1 was
written, and the FY27 package is *still* anchored to it (§5). To adopt it you have to accept a point with no
walk-forward score at all, two fitted parameters that cannot be error-bounded, and a lap geography (North
America only) that two SEC-filed shareholder letters contradict (§4). PREREG D-02 and DEC-0004 both went the
other way.

**149.0m (+11.5%) — the Street.** True if 3Q26 accelerates from 2Q26's +10.34%. That requires the product
bundle to still be adding in its lap quarter, September to have been strong enough to offset a hotel RevPAR
family that faded from +8.2% in July to about +4% by mid-August, and the booking-date KPI to run above a
stay-date series that reads +10.0% before correction. No measured series in this repository is accelerating
through August. The adopted distribution puts P(≥147.0m) at 0.386 and P(≥147.8m, a genuine acceleration) at
0.260. Our claim is not that the Street is irrational — it is that the Street's number is the guide carried
forward, and that management would have to hit a guide that no independent series supports.

**Grade.** D1 is **B**. Its strongest known failure, verbatim from D1 §6: "**the index's central reading is
+10.0%, which is 147.0m — the Street's lowest estimate — and 146.3m exists only because we subtract the
index's own +0.52pp walk-forward bias, a correction estimated on ten quarters whose training years fail their
vintage-constancy test and whose W1 counterpart would subtract +1.63pp instead and put the line at 144.8m.**"

---

## 4. 4Q26: why 131.8m, word by word

The committed line is **131.8m, +8.12%**, band 131.7–132.7 (**DEC-0019**). It is one subtraction from one
reference on one printed base.

### 4.1 The arithmetic

```
4Q25 printed base            121.9m          (abnb_driver_history_quarterly.csv)
team reference growth        +8.90%          (PR #32 NA-lap model, base, = 132.7m)
ex-NA fee/cancellation lap   −0.78pt         (45% midpoint of a 40–50% split)
------------------------------------------------------------------
4Q26 base                    +8.12%   ×121.9m  =  131.8m
```

A rounding note, because a careful reader will find it. PR #32's own figure is **8.9**; 132.7m on a 121.9m
base is actually **+8.859%**. The adopted 8.12 = 8.90 − 0.78, so the base carries PR #32's rounding.
`06_pass_line.csv` records this explicitly: its sixth test re-derives the 4Q26 exit on the v2 decomposition
at **8.157** against bridge v3's 8.12 and passes it, with the note "(rounding of 132.7/121.9 in N memo)".
D2 §2's own band top is quoted as **8.86**, the un-rounded case A.

### 4.2 Where the 0.78 comes from

The lap is **one assumed parameter**: the share of the ex-North-America product bundle that the
**cancellation redesign and single-fee tranche 1** account for. `analysis/src/overnight2/D1_rnpl_cohort_scenarios.py`
writes `data/processed/overnight2/D/D1_exna_4q26_gap.csv`:

| ex-NA share of the ex-NA bundle | points missing from 4Q26 | adjusted 4Q26 | level | consistent with the 4Q25 disclosure? |
|---|---:|---:|---:|---|
| 40% | 0.70 | 8.20% | 131.9m | yes |
| **45% (the adopted midpoint)** | **0.78** | **8.12%** | **131.8m** | yes |
| 50% | 0.88 | 8.03% | 131.7m | yes |
| 70% | 1.22 | 7.68% | 131.3m | **no** — implies a 4Q25 bundle of 2.6–3.1 points against "over 200 basis points" |
| 100% | 1.75 | 7.15% | 130.6m | **no** — same reason |

**The CFO sentence that pins it.** 4Q25 call, ledger row **D014** (Mertz): "these three features delivered
**over 200 basis points** of growth in nights booked and roughly 300 basis points of growth in GBV in Q4."
In 4Q25 ex-NA RNPL was **zero** — it had not launched internationally — so the ex-NA bundle in that quarter
is the fee and cancellation legs **alone**. Requiring the model to reproduce "over 200bp" caps the split.
The out-of-sample check (D2 §6): 40% → 2.05pt, 50% → 2.23pt, both pass; 70% → 2.58pt and 100% → 3.10pt both
fail. 4Q25 is a quarter PR #32 was **not** fitted on, which is what makes it a check rather than a
calibration. (By contrast the 1Q26 agreement — bundle total 3.1pt against management's "approximately three
points" — is **agreement by construction**, because PR #32 is fitted on it.)

**The SEC-filed geography.** `analysis/src/overnight2/D0_rnpl_statement_ledger.py` builds
`rnpl_statement_ledger.csv` from the 3Q25 and 4Q25 shareholder letters
(`data/raw/letters/3Q25_d40503dex991.htm`, `4Q25_d58192dex991.htm`) and the 4Q25 / 1Q26 calls — 60 dated
statements, 57 verified verbatim. Rows **D012, D013, D024, D060** date the cancellation redesign and both
fee tranches to **October–December 2025** and describe them as **global**: "In October, we announced new
cancellation policies…"; PMS hosts to the 15.5% single fee **from October 2025**, most remaining single-fee
hosts **from December 2025**. PR #32 laps those two legs in **North America only**, on an assumption that is
**undated and unstated** in its own code.

**The provenance asymmetry, which must be said before a judge finds it.** The **dates** (D012, D024, D060)
are `official_or_mirror = official` — SEC-filed letters. The **magnitude pin** (D014) is
`official_or_mirror = mirror` — a stockanalysis.com transcript page, not the IR PDF. The dates are solid;
the magnitude is not. D2's own "strongest known failure" is exactly this.

### 4.3 Case A vs case B

- **Case A** — PR #32's NA-only lap: **132.7m, +8.86%** (quoted by PR #32 as 8.9).
- **Case B** — the global lap on the filings' own dates: **131.8m, +8.12%**.

**DEC-0019 adopts case B**, with case A as the **top of the band**, not a rejected case. The reasoning in
D2 §8 choice 1, including the part nobody had written down: **the model already runs on it.**
`h2_bridge_v3_rebased_lines.csv` carries `adopted = 8.12`, `adopted_mm = 131.8`, `band_lo = 8.0`,
`band_hi = 8.86`; `rnpl_v2`'s registered `exna` path carries `q4_nights_m = 131.7739`; and
`adopted_q4_states_v2.json`'s V1 centre is **8.1** with `q4_centre_source` = "team case B global lap 8.1".
Adopting case B was a **ratification of the live model, not a change to it**; rejecting it would have
required rebuilding three artefacts.

One provenance curiosity worth knowing: `REBASE_h2_bridge_v3_nights_adr.md` (12 Sep) records that "4Q26
nights were already at 8.1% **by coincidence**" — bridge v1's unfitted "half lap" overlay had landed on the
same number as the case B global lap — "so that line's value does not move but its source does."

In dollars the disagreement is small: at N memo 2's 4Q26 ADR of **$173.55**, the whole case-A-vs-case-B
nights gap is about **$21M of revenue** ($3,115M vs $3,137M). N memo 2's own words: "the lap decision is a
nights-growth-rate question, not a revenue-dollar question."

### 4.4 Why the cancellation drag is NOT added in base

`D2 §2a` carries `cancel_drag_pp, base, 4Q26 = 0.00`, "excluded by construction".

The reason is the **D1 no-stacking rule**, carried forward. There are two routes to a 4Q26 number:

- **Case B** (adopted): the 8.90 reference minus the **lap only** = **8.12% / 131.8m**.
- **The unified RNPL module** (`rnpl_nights_module.csv`, row base/4Q26): the same 8.90 reference minus
  **M1 level lap −0.590, M2 pull-forward −0.156, M3 cancellation deferral −0.095, M4 propensity drag
  −0.446** = **−1.288 total → 7.61% / 131.2m**.

The module's 7.61 **already is** lap-plus-drag. Adding a drag to case B's 8.12 and then quoting 7.61 as a
separate scenario would count the same ~0.5pt twice. D1 §7 states the rule for 3Q26 ("the +9.49% module and
this +9.5% are two routes to the same level, not two effects to be stacked") and D2 §7 carries it into 4Q26
("case B's 8.12 and the module's 7.61 are **two routes, not two effects**; the 0.51pt between them is the
cancellation tail, and it belongs in the short scenario only"). DEC-0019 states it in the decision row:
"cancellation drag not stacked in base (D1 no-stacking rule)".

There is a second, better reason, and it is the honest answer to "how do you know it is not demand": **the
drag is the only leg with a demand interpretation, and it is the leg with no empirical support.** The
pre-registered 34-market calendar study found no RNPL cancellation signature (§6.2). The cohort engine's own
central cells put the 4Q26 drag at **−0.14 / −0.28 / −0.57 / −0.85** at +1 / +2 / +4 / management-implied
propensity, with a full-grid range of **−1.36 to −0.08** — two to fifteen times smaller than the level lap.

### 4.5 The β = 0.5 carry question

`adopted_q4_states_v2.json` (A12 rev 2, 17 Sep) defines its 4Q26 centre conditionally:
**`q4 = 8.1 + 0.5 × (Q3 − 9.5)`**. At the centre it sets Q3 = 9.5, so no carry applies — but the **8.1 was
built in a world where Q3 was 9.89** (PR #32's reference). So the object uses a carry coefficient of
**0.5 at the margin and 0.0 at the centre**, which D2 §7 conflict 2 calls "not a rule, it is two rules".

Applying the object's own β to the 0.39pt 3Q26 downgrade gives **7.93% → 131.6m**; at β = 1.0 it is
**7.73% → 131.3m**. That is a −0.2 to −0.4pt question on the line the memo trades, worth about $5M of
revenue at β = 0.5.

**Base today is no carry (8.12).** D2's recommendation is (b), carry at β = 0.5, or (a) with the
inconsistency footnoted. The argument against full carry: much of the 3Q26 gap is the reviews index's own
**measured bias**, which has no reason to persist into a quarter the index does not cover. This is an open
item, not a settled one, and it is the cleanest single thing that would move the 4Q26 line.

### 4.6 The Street bar, and the band

**Street 4Q26 = 134.0m** (Bloomberg MODL, 12 Sep 2026, n = 28), which is **+9.93%** on the 121.9m base.
V1 calls this row "clean" — unlike 3Q26, it matches the brief's figure exactly with no vendor/date mix-up.

The adopted 4Q26 print object is a mixture (0.5 decomposition / 0.3 guide route / 0.2 Street) with
**mean 8.61, sd 2.28**, P(≥134.0m) **0.307**, P(≤131.0m) **0.3089**, P10 5.56 / P90 11.44. Note DEC-0019
did **not** take that mean as the model input, and D2 §8 choice 3 says why: the object is 20% weighted to
the Street anchor, so using it as our input would import the Street's bar into a variant-view model. The
8.61 mean is the right object for *pricing the risk lines* and the wrong one for the model input.

For reference, management repeating "low double digits" for 4Q26 would be **≥ +10.0% = 134.1m** — one tenth
**above** the Street's bar, so the breaker case and the sell-side bar coincide almost exactly, as they do on
3Q26.

**One conflict to fix before any card freezes.** `D1_prereg_thresholds.csv`'s 4Q26-guide row says the
omitted global lap is "worth **0.9 to 1.8 points**". `D1_exna_4q26_gap.csv`, written by the **same script in
the same run**, marks the 0.7-share (1.22pt) and 1.0-share (1.75pt) rows as
`consistent_with_4q25_disclosure = no`. The admissible range is **0.70 to 0.88**. Two files from one folder
disagree by a factor of two.

**Grade.** D2 is **B**. Its strongest known failure, verbatim: "**the entire 0.78-point lap rests on one
assumed parameter — the ex-NA share of the ex-NA bundle — pinned only by a single CFO sentence that exists
in this repo as a stockanalysis.com mirror rather than the official IR transcript, and neither of the two
cases it separates (8.12 vs 8.86) can be confirmed or refuted by the 5 Nov guide, because our own
pre-registered thresholds put both of them inside the 'inconclusive' band.**"

---

## 5. 2027: why the bridge path

**DEC-0025**: the 2027 quarterly base is the bridge path **169.02 / 157.10 / 155.96 / 139.77**, FY27
**621.84m, +6.64%**, with the lap-schedule 1Q27 (167.1) carried as named open item **D-11**.

### 5.1 How the bridge builds the quarters

Two scripts in sequence.

`analysis/src/h1_to_h2_bridge_v3.py` (12 Sep) sets the **2H26 exit**. Its v3 change is the one that matters:
the v1/v2 pattern-plus-unfitted-overlays construction (RNPL lap −1.5/−2.5, World Cup +0.5) was **replaced**
by the team baseline for 3Q26 (+9.9% / 146.8m) and the ADR v3 N memo case B for 4Q26 (+8.1% / 131.8m). The
old overlays are kept as comparison rows with **pts = 0 applied**.

`analysis/src/margin_build/06_fy27_path_v2/run.py` then builds each 2027 quarter **in growth space**, not
in levels. `06_nights_build.csv`, base scenario, is the whole model in four rows:

| quarter | NA share (prior yr) | NA y/y | ex-NA pre-lap y/y | NA contribution | ex-NA contribution | fee/cancel lap | RNPL lap | event | **total y/y** | sensitivity: no ex-NA lap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1Q27 | 0.291 | 2.31 | 10.773 | 0.672 | 7.638 | −0.742 | −0.363 | **+1.0** | **8.206** | 9.311 |
| 2Q27 | 0.291 | 2.31 | 10.452 | 0.672 | 7.411 | −0.742 | −0.907 | **−0.5** | **5.934** | 7.583 |
| 3Q27 | 0.288 | 2.31 | 10.131 | 0.665 | 7.213 | −0.742 | −0.907 | 0.0 | **6.229** | 7.878 |
| 4Q27 | 0.282 | 2.31 | 9.810 | 0.651 | 7.043 | −0.742 | −0.907 | 0.0 | **6.045** | 7.695 |

Those growth rates are then compounded onto the prior-year levels to give `nights_mm` in
`06_revenue_path_wide.csv` / `06_revenue_path_3q26_4q27_v2b.csv`, and summed in
`06_annual_fy26_fy28_v2b.csv`: **FY27 = 621.8414m, +6.642%**, on **FY26 = 583.1113m**.

**The regional path.** The NA rate **+2.31%** is `na_nights_lap_scenarios.csv`, row "base: no product lever",
column 2027 = **0.0231** — the output of `analysis/src/na_nights_reconciliation.py`, a script whose own
docstring is a record of the disagreement it exists to resolve: "the model gets US +3.3% for 2026 against
WS10's NA +7%", and it "does not argue" but inverts the choice model to ask what each lever would have to be
to reach the team's NA path. The ex-NA pre-lap rate is WS10's FY27 regional rate, **phased linearly** from
the WS10 4Q26 ex-NA rate so that the four-quarter mean equals WS10's annual figure. That phasing rule is
flagged in `06_assumptions.csv` as `exna_phasing_rule`, `is_judgement = True`, with the note "WS10 gives only
an annual FY27 rate; a linear decay avoids a jump at 1Q27". The file carries **55 assumptions, 10 of them
judgement**.

**The lap treatment.** Two separate lap terms, and the distinction is the whole of D-11:

- **fee/cancellation, −0.742pt, constant in all four quarters.** This is the 4Q26 ex-NA lap **carried
  forward**, not re-applied. It is already inside the adopted 4Q26 exit; holding it flat keeps the level
  effect in place without charging it twice.
- **ex-NA RNPL, −0.363 in 1Q27 and −0.907 from 2Q27.** The 1Q27 figure is the full −0.907 at a **40%
  phase-in**, because the international rollout went live 17 Feb–4 Mar 2026 — roughly the last 5–6 of 13
  weeks of 1Q26 — so the 1Q27 lap is partial. `06_assumptions.csv`: `exna_rnpl_lap_fraction_1Q27 = 0.4`,
  "Fraction is judgement", `is_judgement = True`. **Assumed.**

**D-11, the double count.** PR #32 applies a flat **−1.75** points from 1Q27 through 4Q27 and **nothing** in
4Q26. If the 4Q26 ex-NA lap is adopted **and** PR #32's 1Q27 row is used as-is, the fee-and-cancellation leg
is charged twice — about **0.8pp**. The 06 build avoids this by construction (constant −0.742 rather than a
fresh lap), and D2 builds all of its own 1Q27/2Q27 descriptive rows on the `exna_lap = False` reference for
the same reason. Anyone rebuilding FY27 from PR #32's `exna_lap = True` row will double count.

**Events.** Middle East base **+1.0pt in 1Q27**; World Cup lap **−0.5pt in 2Q27** in base (−0.75 / 0 in the
other scenarios).

### 5.2 The comparison quarters — and a correction

The memo says "1Q27 guides against a **+17.9%** comp; 2Q27 against **+16.5%**", and D2's descriptive 1Q27 and
2Q27 rows repeat those figures. **Those are revenue comps, not nights comps.**
`docs/rnpl-short-audit/02_fy27-decomposition-rnpl-synergy.md` §3 labels its own row "**FY26 comp
(revenue)**: 1Q27 +17.9%, 2Q27 +16.5%, 3Q27 +16.6%, 4Q27 +12.0%", and
`docs/rnpl-short-audit/05_quality-of-growth-study.md` gives the same quarters column by column:

| quarter | nights | GBV | revenue |
|---|---:|---:|---:|
| 1Q26 | **+9.2%** | +19.2% | **+17.9%** |
| 2Q26 | **+10.3%** | +15.7% | **+16.5%** |

**The nights comps that 1Q27 and 2Q27 actually lap are +9.2% and +10.3%.** (156.2 ÷ 143.1 and 148.3 ÷ 134.4
on the printed history.) The +17.9/+16.5 pair belongs to the revenue line, where it is a genuinely striking
comp. On the nights line it is a mis-attribution waiting to happen, and it should be corrected wherever it
appears next to a nights number.

### 5.3 The 1Q27 open item: 169.0 vs 167.1

Two constructions, 1.9m nights and 1.24pt apart:

| construction | 1Q27 | 2Q27 | source |
|---|---:|---:|---|
| **bridge path (adopted, DEC-0025)** | **169.02 / +8.21%** | **157.10 / +5.93%** | `06_nights_build.csv` |
| D2's ledger-dated lap schedule (descriptive) | 167.1 / +6.97% | 157.8 / +6.42% | D2 §2a, built on the `exna_lap = False` reference 8.17 plus the ledger-dated lap −1.07 to −1.32 (1Q27) and −1.57 to −1.93 (2Q27) |
| unified RNPL module, base | 166.3 / +6.47% | 157.9 / +6.44% | `rnpl_nights_module.csv` |

The gap is mostly two things: the 06 build's **+1.0pt Middle East event term**, which D2's schedule does not
carry, and the **size of the 1Q27 lap** (−0.363 at a 40% phase versus the ledger's −1.07 to −1.32). DEC-0025
adopts the bridge path and carries 167.1 as **D-11**, the named open item for the FY27 discussion.

**One thing nobody has written down, and it belongs in the FY27 discussion.** D2's pre-registered 11 February
test says a 1Q27 guide **at or above +8.2% (169.0m) falsifies the RNPL module outright**, because that
requires both the partial ex-NA lap and the pull-forward reversal to be absent (D2 §2a, breaker row; §6 last
row). **The adopted bridge base for 1Q27 is 169.0178m, +8.206%** — numerically at the falsifier. The two
objects are not the same construction (the bridge carries a +1.0pt Middle East event and only a 40% RNPL
phase-in; the module's 8.17 reference carries neither), so this is not a contradiction in arithmetic. But it
means **our own base case for 1Q27 sits on our own pre-registered kill line for the RNPL module**, and a
judge who reads both files will ask about it. Either the event term, the phase fraction, or the falsifier
threshold has to move before 11 February. Flagged, not resolved.

D2 also flags an ordering problem in the descriptive rows that has to be resolved before they are used
anywhere: at 2Q27 the **lap-only base (6.42%) is harsher than the lap-plus-tail short (6.44%)**, because by
2Q27 the module's own M1 (−1.550) is gentler than the ledger's dated full lap (−1.57 to −1.93) — the module
nets the July 2026 expansion against it. "Today they cross."

### 5.4 FY27: +6.64% vs +6.42% vs +8.17%

**+6.64% (adopted).** The sum of the four bridge quarters. It sits between PR #32's two never-chosen-between
cases, and it is the only one of the three that was ever summed to real quarterly levels.

**+6.42% — the RNPL global lap (`alt_rnpl`).** PR #32's flat "global lap" rate, re-derived **byte-for-byte**
inside D3's own reproduction at `06_pr32_rederivation.csv`, row "PR32 total base FY27 nights level,
exna_lap=True" = **621.6mm** on PR #32's own **584.1mm** FY26 base = **+6.42%**. Independently corroborated
to 0.02pp by two unmerged constructions in `docs/rnpl-short-audit/02_fy27-decomposition-rnpl-synergy.md`
(PR #32's own global lap +6.42%; Jessie's plateau-plus-drag +6.52%), and the unified module's own FY27 is
**+6.41%**. **Correction on the record:** `docs/pitch-model-v2/LINES.md` attributes "FY27 nights +6.4%" to
`05_backtests/ALPHA_F_RNPL.md`, **which contains no FY27 nights figure** — that file is a Q3/Q4-2026
excess-unpaid-share stress test. The number is real and reproducible; the pointer is wrong. D3 states the
correction rather than silently editing another lane's file.

**+8.17% — the lap-treatment flip.** One unresolved reading: does WS10's own FY27 regional rate **already
embed** a product-bundle deceleration, or is the ex-NA RNPL lap **additive on top of it**? The 06 build
assumes additive. The independent second build, `06v_fy27_path_check` (14 Sep), ran the other reading as
`base_no_exna_lap_2027`: **FY27 nights +8.17%**, revenue $15,964M / +11.9%, which is **$167M and 1.2pp above
base** and "just outside the B3 band". That build's own conclusion is "additive, no double count", which is
why base is +6.64%. But D3's §6 is blunt about what this is: "not a data revision, **a reading of a
qualitative rationale string**", and flipping it moves the line **1.5pp**. The quarterly version is the
`sens_no_exna_lap_case_A_pct` column above: 9.311 / 7.583 / 7.878 / 7.695.

For context on where else this sits: B3's own FY27 volume line is four flat regional rates with **no lap, no
tail, no pull-forward** — **+9.4558% total nights** — which is 1.3 points above the top of the RNPL-aware
FY27 range.

### 5.5 What is unbacktested about all of it

Everything. D3 §6's window column reads "**n/a — forward object, no historical window exists**": W1 and W2 do
not exist for a year that has not printed. Three things stand in for a test:

1. **An internal pass line, 7/7** (`06_pass_line.csv`): quarterly sums equal annuals; 1Q27 within 2 points of
   the 4Q26 exit (gap 0.09); FY27 base revenue inside B3's +9.18–11.52% band (10.94); 2027 seasonal shares
   within 1pt of the 2023–25 mean (max deviation 0.23pt); every number traceable to an input file (55 rows,
   10 judgement). These are arithmetic and consistency checks, not forecast scores.
2. **An independent second build.** `06v_fy27_path_check` rebuilt the same nights logic from the same named
   inputs **before reading WS06's script or note** and got **+6.56% (621.4mm)** — 0.08pp / 0.4mm away, both
   differences traced to two named, disclosed judgement calls (the 1Q27 RNPL phase fraction 0.40 vs 0.423,
   and the ex-NA phasing shape). It also confirms that WS10 does **not** already embed the RNPL lap, i.e. no
   double count.
3. **A reproduction receipt.** D3's re-run of `h1_to_h2_bridge_v3.py` and `06_fy27_path_v2/run.py` is exit 0,
   0.7s, and **byte-identical on every quoted cell** — `06_nights_build.csv`, `06_revenue_path_wide.csv`,
   `06_annual_fy26_fy28.csv`, `06_pr32_rederivation.csv` do not appear in the receipt's `changed` list at
   all. That proves the arithmetic is stable; it proves nothing about whether the assumptions are right.

**And the stale anchor.** The whole FY27 path is still anchored to the pre-DEC-0004 team baseline
146.813m / +9.89% for 3Q26 (`06_revenue_path_3q26_4q27_v2b.csv`, `3Q26,base,nights_mm` = 146.813, source
"bridge v3 adopted"). D3 §7 conflict 1 is precise about the consequence: the FY27 quarterly build **does not
chain arithmetically off the literal 3Q26 level** — it is built from WS10's regional y/y rates and prior-year
NA shares — so the 0.5mm / 0.39pp gap does not mechanically propagate into +6.64%. What it does touch is the
**denominator** (FY26 583.11m instead of 582.62m, so FY27 y/y would be **+6.73%** rather than +6.64%) and the
narrative continuity, and the `06_pass_line.csv` exit checks are computed against the superseded base. D3
could not fix it: `h1_to_h2_bridge_v3.py` and `06_fy27_path_v2` are outside its lane, and its recommendation
is a cross-lane re-run request, cost 0.7 seconds.

**Grade.** D3 is **B**. Its strongest known failure, verbatim: "**the FY27 nights number cannot be
backtested (it is a forward build on judgement, not a fitted or historically-scored object, so it fails the
'survives both W1 and W2' bar by construction) — and the single largest judgement inside it, the ex-NA RNPL
lap phasing, is a coin-flip on one unresolved question ('does WS10's own FY27 regional rate already contain a
product-bundle deceleration, or is the lap additive on top of it?'); WS06v's own sensitivity answers
'additive, no double count' and gets +6.64%, but flipping that one judgement — not a data revision, a reading
of a qualitative rationale string — moves FY27 nights to +8.17%, which is closer to PR #32's un-adopted
NA-only case and just outside the pre-registered B3 revenue band that today's number sits comfortably
inside.**"

---

## 6. How the thesis catalysts enter this line

### 6.1 RNPL (Reserve Now, Pay Later)

**The bundle lift.** Management quantified the three-feature bundle twice and then stopped:

| quarter | what management said | ledger row | source quality |
|---|---|---|---|
| 4Q25 | "these three features delivered **over 200 basis points** of growth in nights booked and roughly 300 basis points of growth in GBV in Q4" | D014 | **mirror** (stockanalysis.com transcript) |
| 1Q26 | "**approximately three points** of nights booked growth and approximately four points of GBV growth in Q1" | D032 | call |
| 2Q26 | **no figure.** RNPL's share of GBV quoted instead ("over 20%") | — | letter |

The "~3 points in 1H26" is the 1Q26 figure. **Where it enters this line numerically:** it is the thing being
lapped, not an additive term. PR #32's two fitted parameters (**+2.40** RNPL and **+2.29** fee-plus-
cancellation points of NA nights) reproduce the 1Q26 ~3.0 global points **by construction**, which is why
D2 §6 labels that row "agreement is by construction" rather than a test.

**The eligibility timeline.**

| date | event | source |
|---|---|---|
| mid-Aug 2025 | US launch: US guests, domestic, flexible/moderate cancellation policies | memo v3 RNPL table; ledger |
| Oct 2025 | cancellation-policy redesign announced, **global**; PMS hosts to the 15.5% single fee | letters, ledger D012/D024 |
| Dec 2025 | most remaining single-fee hosts migrate | letter, ledger D060 |
| 17 Feb – 4 Mar 2026 | international rollout: **UK 18 Feb, Australia and APAC 23 Feb, Canada 4 Mar**; excluded by payment currency BRL, INR, TRY | `docs/overnight2/SYNTHESIS.md` §1 |
| July 2026 | **eligible booking types expanded** — unnamed and unsized by the company | ledger **D044** |

The July 2026 expansion is, in D2's own words, "**the largest unquantified offset in the model**". It is
carried in the module at **+0.1 to +0.3 points** — **assumed** — and D2 says a bull could reasonably carry it
higher. In the module's 3Q26 row it is netted **inside M1**, which is why M1 for 3Q26 is a **positive
+0.304** despite being the US lap quarter.

**The lap timing.** US **3Q26** (partial — "beginning of Q3"; the audit sizes the partiality at **+0.35**
against the short); global cancellation and fee legs **4Q26**; ex-NA RNPL **1Q27** (partial, 5–6 of 13 weeks)
and **full from 2Q27**.

**Exactly where RNPL appears in the base numbers:**

| period | RNPL's numerical appearance in the base |
|---|---|
| 3Q26 | **Not as a subtraction.** The base is the index read minus the index's own bias. RNPL enters only through the *corroborating* module route, which reaches the same 146.3m as 9.89 reference − 0.396 (M1 +0.304, M2 −0.113, M3 −0.019, M4 −0.568). Because the routes are alternatives, the base does not contain an RNPL term at all. |
| 4Q26 | **−0.78pt, and that is the whole catalyst in this quarter.** The ex-NA fee-and-cancellation legs, dated by the letters. |
| 1Q27 | **−0.742pt** (fee/cancel, carried) **−0.363pt** (ex-NA RNPL at 40% phase-in) |
| 2Q27–4Q27 | **−0.742pt** (fee/cancel, carried) **−0.907pt** (ex-NA RNPL, full) |

**The cancellation tail: flow versus stock.** The gross booking lift scales with the **flow** of new RNPL
bookings, which has flattened (memo v3: the eligible pool roughly tripled while the disclosed share moved
from "roughly 20%" to "over 20%"). Cancellations scale with the **stock** of live unpaid bookings reaching
their payment deadline, which is still growing. **46–49% of a quarter's excess cancellations arrive from
earlier booking cohorts** (`docs/overnight2/SYNTHESIS.md` §2 D), and reported Nights and Seats Booked
subtracts a cancellation in the quarter it occurs, not the quarter it was booked. The cohort engine puts the
3Q26 drag at **−0.2 to −0.9 points** (memo v3; the full D grid is −0.10 to −1.37 for 3Q26 and −0.08 to −1.36
for 4Q26, central cells −0.14 to −0.85). The live stock behind it, from the balance-sheet work: **17 to 28
million unpaid nights at 30 June** (13.6–37.3 across the divisor and ADR stress) — the earlier 7–19 million
figure is **withdrawn**. And the fact is official, not inferred: the 2Q26 10-Q MD&A says in audited language
that RNPL bookings "have experienced **higher cancellation rates** than historic bookings".

**The explicit statement, which the memo must carry:** **the base carries the lap and does not carry the
drag.** `cancel_drag_pp, base, 4Q26 = 0.00` by construction (§4.4). The drag is what separates the base from
the short (7.61%), and DEC-0020 defers the short. Anyone who adds a cancellation drag on top of the base is
double-counting.

**The 5 Nov tells** (`D1_prereg_thresholds.csv`, summarised in the overnight2 D note §5):

| tell | supports our case | weakens it | inconclusive |
|---|---|---|---|
| a quantified **bundle contribution** for 3Q26 | none given, or ≤ **1.5 points** | ≥ **2.5 points** | qualitative update only |
| an **RNPL share of GBV** disclosed for 3Q26 | flat or down vs 2Q26 while nights decelerate | ≥ **25%** with nights ≥ 10% | 21–24% |
| 3Q26 quarter-end **unearned fees, y/y** | ≤ **−3%** (below ~$1,765M) | ≥ **+6%** (~$1,930M) | −3% to +6% |

Two corrections travel with the unearned-fees row and both are on the record. First, management **predicted**
unearned fees would be **higher** in Q3 (1Q26 letter), so a weak print contradicts management. Second, the
11 Sep proposal to score funds payable instead of unearned fees was itself **REFUTED on adversarial
verification**: the FY2025 10-K Note 2 says "Host and guest fees are recorded as cash with a corresponding
amount in unearned fees", so the host-only fee sits in unearned fees exactly as the guest fee did, and the
migration moves the line **up** 3–4%, not down. **Unearned fees is the FX-clean, migration-neutral line;
funds payable is the noisy one** (±8.7-point annual FX swing). The corrected rule is to score
**(3Q26 unearned fees y/y) − (3Q26 GBV y/y)**: ≤ **−18 points** supports, −12 to −18 is in line with 1H26,
wider than −8 weakens.

### 6.2 The nights deceleration

**The sequence the base implies, against the Street's:**

| | 2Q26 (printed) | 3Q26 | 4Q26 | 1Q27 | 2Q27 | 3Q27 | 4Q27 |
|---|---:|---:|---:|---:|---:|---:|---:|
| **our base** | +10.34% | **+9.5%** | **+8.12%** | **+8.21%** | **+5.93%** | **+6.23%** | **+6.05%** |
| Street | — | **+11.5%** (149.0m) | **+9.93%** (134.0m) | flat ~+11% revenue in every quarter | | | |

The step from 2Q26 to 4Q26 is **−2.2 points**; from 2Q26 to 2Q27, **−4.4 points**. The Street's 3Q26 bar is
an *acceleration*.

**What the deceleration is made of — and what the record can and cannot separate.**

The record **can** separate, because it is dated rather than fitted:

- **4Q26: the full 0.78pt step down from the 8.90 reference is lap arithmetic.** It comes from two
  SEC-filed shareholder letters dating the cancellation redesign and fee tranche 1 to Oct–Dec 2025 and
  describing them globally. A level gain that went live in Oct–Dec 2025 lifts y/y growth in 4Q25–3Q26 and
  then stops lifting it from 4Q26, **whatever demand does**. That is the entire mechanism.
- **2027: the named lap terms are −0.742 (fee/cancellation, carried) and −0.363 / −0.907 (ex-NA RNPL).**
  The 2Q27 step of **−2.272pt** from 1Q27 decomposes exactly: the RNPL phase-in deepening **−0.544**, the
  event term swinging from +1.0 to −0.5 (**−1.500**, i.e. the loss of the Middle East base plus the World
  Cup lap), and **−0.227** of ex-NA contribution as the ex-NA rate decays 0.321pt. Those three sum to
  −2.271.

The record **cannot** separate lap from demand for the rest of it:

- The residual deceleration in 2027 is **WS10's own ex-NA rate decaying from 10.773 to 9.810** and the NA
  rate **held flat at +2.31**. Those are forecast assumptions, not measurements.
- **The one test that would have shown a demand/cancellation signature returned a null.** The 34-market
  calendar study was pre-registered: if RNPL generated excess cancellations, listings outside the US should
  have reopened more after the **17 February 2026** international launch than US listings. The contrast is
  **+2.06pp** (bootstrap 0.69 to 3.47 on 2,000 reps), **permutation p = 0.26** — not significant at any
  conventional threshold — on **32 markets (25 non-US, 7 US)**. It **collapses when one 29-listing market is
  dropped**, and what moves it is **Australia**, which is in the opposite season. The pre-rollout US level is
  also higher than the non-US level, so the cross-section partly reflects composition. The line of attack was
  **retired** and the null kept on the record.
- A second series was retired for the same reason: the calendar **booking-pace flow** correlates **−0.43**
  with disclosed nights and **−0.53** with its acceleration on n = 5 — **sign inverted**. It is a direction
  check only and never a number (D1 §4, last row).

So the claim this line supports, and the only one it supports, is **D2's**: "this is a **comp-arithmetic
claim, not a demand claim**". The pre-registered identification column already concedes in writing that "a
guide cut cannot be attributed to cancellations without management saying so". And the hard limit:
**both** of our 4Q26 cases (8.12 and 8.86) fall **inside our own pre-registered inconclusive band (7.6–9.4%)**,
so the 5 Nov guide alone cannot separate them.

### 6.3 The World Cup

Management called the 2026 World Cup the largest event in Airbnb's history, said event bookings cluster close
to the games, **never sized it**, and framed 2Q26 as "no single product" (memo v3). WS10's own note is on the
record that the World Cup gives **no lift to 3Q26 booked nights**
(`nights_baseline_reconciliation.csv`, first row's note).

**Where it sits in this line:** nowhere in 3Q26 and nowhere in 4Q26. It enters **exactly once**, as the 2Q27
event term **−0.5pt** in `06_nights_build.csv` (base; −0.75 and 0 in the other scenarios) — the **assumed**
lap of an unsized pull-forward. That −0.5 is about a fifth of the 2.27pt step down from 1Q27 to 2Q27.

Historical note so nobody re-imports it: bridge **v1 and v2 carried an unfitted World Cup +0.5 overlay on
3Q26/4Q26**. Bridge v3 retired it (pts = 0 applied) when it re-based on the team baseline and case B. The
current line carries no World Cup term in 2026 at all.

### 6.4 FX

**FX does not enter this line.** Nights is a unit count. The reviews index is built from **review counts**,
not prices; `E4_build_index.py` and `E6_nowcast.py` contain no currency term, and `06_nights_build.csv` has
no FX column. D3 §3 step 2 states it directly: the ADR v3 card and the FX kernel "feed the 2H26 exit only,
**not nights directly**".

The one channel by which FX **could** have touched nights was measured and is zero at spot. Overnight2 WS-B
fitted a mix elasticity of **~0.11pp of regional differential per 1pp of inbound purchasing power** (n = 28,
permutation p 0.04) and found that at current spot "**it nets to nothing for total nights**" (and −0.06pp on
ADR). The identified piece is US **outbound** at a two-quarter lag (r +0.89 on BEA); US **inbound** has the
wrong sign because visa fees, tariffs and the Canadian boycott moved against the dollar in 2025–26.

FX belongs to **ADR and revenue**: DEC-0010 sets 4Q26 revenue FX at **+0.98pp** base, and DEC-0008 governs
the ADR card. Those are not nights numbers and must not be carried across.

### 6.5 Fee migration and the cancellation-policy redesign

**Any nights effect assumed? For the ongoing migration, none.**

- The **October 2025 cancellation redesign** and **single-fee tranche 1** are two of the three legs **inside**
  the 0.78pt 4Q26 lap and the −0.742pt 2027 term. That is a **level lap**, i.e. the removal of a prior-year
  boost, not a forward-looking nights effect.
- The **second fee tranche** — the continuing migration of hosts to the 15.5% host-only fee — is carried at
  **0.0 points of nights**, on PR #32's own fee-elasticity work (D2 §7, near-miss check ii). No nights uplift
  and no nights drag is assumed for tranche 2. The fee migration's live deadlines (15 Sep for non-EEA-resident
  hosts, 13 Oct for EEA+CH) are on the record in the fee notes and change nothing on this line.
- The fee-migration term **K** is an **ADR** object, not a nights object: DEC-0008 adopts ADR card v3
  **without K**, carrying K (+0.17pp) as a labelled sensitivity. It does not appear in nights.
- The **2Q26 Strict-to-Firm cancellation-policy migration** is a 2026 policy change that **no team model
  carries**. The overnight2 D note lists pinning its scope as open evidence item 4, and flags it as a direct
  confound for the cancellation reading. On this line it is **assumed zero**. It is the clearest named gap in
  the nights build.
- For completeness, because it is adjacent and was wrong once: the claim that the fee migration confounds the
  unearned-fees line was **REFUTED** on verification (§6.1). That affects the 5 Nov tell, not the nights
  level.

**Kill-list check (AGENT_BRIEF §6).** No item on the kill list is quoted as ours anywhere on this line. Four
near-misses were checked and cleared in the dossiers: (i) "the 120-market panel as a nights measurement" is
the Inside Airbnb **listings/calendar** bottom-up panel, a different object from the 123-market **review-date**
stays index used here; (ii) "any FY27 level edge without the +9.2–11.5% band" binds D3/R6 and is respected —
the FY27 base revenue of +10.94% is checked against and sits inside B3's +9.18–11.52% band as a pass-line
test; (iii) the "+4.05% fee uplift" is not used — tranche 2 is carried at 0.0 points of nights; (iv) the
"+10.2% consensus" in older nights notes is our own frozen card and is not used as a Street bar.

---

## 7. What would change this line

### 7.1 The 5 Nov print thresholds (pre-registered)

**3Q26 nights, the forecast test (PREREG INT-02).** SUPPORT if the print lands **inside 8.5–11.0%** *and* the
reviews-index error is below the naive error (naive = 2Q26's **+10.34%**). REFUTE if outside.

**3Q26 nights, the thesis test (PREREG INT-02, second sentence; D §5 row 1).**

- **≤ +8.5% (144.9m or less): supports** the RNPL drag.
- **≥ +10.3% (147.3m or more): weakens** it.
- **8.6% to 10.2%: inconclusive** — which is where our own base (+9.5%) sits.

**The descriptor.** Management's 3Q26 guide is "**low double digits**", a bucket, not a company range. Our
**≥10.0% → 147.0m** mapping is ours. If management delivers the bucket, the number is 147.0m — the same as
the Street's lowest estimate — and we are wrong on the gate. The adopted distribution puts that at **0.386**,
and an outright acceleration (147.8m or better) at **0.260**.

**The band must be settled before the card freezes.** Three bands are in the record for one number:
**8.5–10.0** (memo v3), **8.5–11.0** (SYNTHESIS and PREREG INT-02), and **7.3–11.7** (P10–P90 of the adopted
N(9.5, 1.70)). They are not reconcilable by rounding — 1.5pp wide versus 4.4pp wide. **DEC-0004 resolves it:
8.5–11.0 for the pre-registration and 6 Nov scoring, P10–P90 of N(9.5, 1.70) for the workbook scenarios, and
memo v3's 8.5–10.0 retired.** Publishing 8.5–10.0 while scoring against 8.5–11.0 would score a number we
never published.

**4Q26 guide, 5 Nov.** Implies **≤7.5% supports**, **≥9.5% weakens**, **7.6–9.4% inconclusive** — and both
our own cases (8.12 and 8.86) are inside the inconclusive band, so the guide alone will not settle the lap
question.

**1Q27 guide, 11 Feb.** **≥ +8.2% (169.0m) falsifies the RNPL module outright**, because that requires both
the partial ex-NA lap and the pull-forward reversal to be absent. Note the tension flagged in §5.3: the
adopted bridge base for 1Q27 is **169.0178m / +8.206%**, i.e. at that threshold. The two constructions
differ (the bridge carries a +1.0pt Middle East event and a 40% RNPL phase-in), but the threshold and the
base case have to be reconciled before 11 February.

**The flip rule on this line** (memo v3 Risks): nights **≥ +10.3%** *with* a restated product-bundle
contribution of **2.5 points or more** and we cover. (AGENT_BRIEF §4's flip is the separate take-rate/GBV
one: take rate ≥ 18.10% on GBV ≥ $26.3bn **and** Q4 nights guided "low double digit".)

### 7.2 The September Inside Airbnb dumps

September is **the one month of 3Q26 that nothing we currently hold can see** — the review window stops at
17 Aug 2026. Re-running `E1`–`E6` on the September dumps and re-centring is cheap and mechanical, because the
update rule is already published: centre **9.0 → P(meets guide) 0.28**, **9.5 → 0.39**, **9.9 → 0.48**,
**10.0 → 0.50**.

The condition, from D1 §8 choice 5: **do it if and only if the dumps land by 27 Sep and Krish's raw store is
reachable.** `E1`–`E4` cannot run on this machine — the raw dumps are not here — and a half-finished re-run
two days before submission is worse than a disclosed cut-off. Otherwise: freeze at the 17 Aug window and say
so in the memo.

After that, the next-best evidence is **Marriott's Q3 RevPAR on 4 November**, since hotel RevPAR is the
strongest external feature on this KPI (0.665 W2 / 0.755 W1).

### 7.3 The grades, and each dossier's strongest failure

Every dossier behind this line is graded **B**. Each §6's "strongest known failure", verbatim:

**H0 (printed history) — B.** "the governing (corrected) SBC and diluted-share values for 4Q23/4Q25, and all
five cash-basis cost lines plus D&A for every quarter, trace only to the already-committed
`02_panel_quarterly.csv`, whose generating script exits 1 in this clone on a missing, gitignored raw XBRL file
— so today's exit-0 receipt independently re-derives only the GAAP/SBC-as-filed layer, not the
corrected/cash-basis layer."

**D1 (3Q26) — B.** "the index's central reading is +10.0%, which is 147.0m — the Street's lowest estimate —
and 146.3m exists only because we subtract the index's own +0.52pp walk-forward bias, a correction estimated
on ten quarters whose training years fail their vintage-constancy test and whose W1 counterpart would subtract
+1.63pp instead and put the line at 144.8m."

**D2 (4Q26) — B.** "the entire 0.78-point lap rests on one assumed parameter — the ex-NA share of the ex-NA
bundle — pinned only by a single CFO sentence that exists in this repo as a stockanalysis.com mirror rather
than the official IR transcript, and neither of the two cases it separates (8.12 vs 8.86) can be confirmed or
refuted by the 5 Nov guide, because our own pre-registered thresholds put both of them inside the
'inconclusive' band."

**D3 (FY27) — B.** "the FY27 nights number cannot be backtested (it is a forward build on judgement, not a
fitted or historically-scored object, so it fails the 'survives both W1 and W2' bar by construction) — and the
single largest judgement inside it, the ex-NA RNPL lap phasing, is a coin-flip on one unresolved question
('does WS10's own FY27 regional rate already contain a product-bundle deceleration, or is the lap additive on
top of it?'); WS06v's own sensitivity answers 'additive, no double count' and gets +6.64%, but flipping that
one judgement — not a data revision, a reading of a qualitative rationale string — moves FY27 nights to
+8.17%, which is closer to PR #32's un-adopted NA-only case and just outside the pre-registered B3 revenue
band that today's number sits comfortably inside."

**V1 (Street) — the dossier grades itself C; DEC-0012 accepts B**, on the grounds that the frozen L0 register
tests (exit 0) are this line's reproduction and that `consensus_stamp_v2`'s verify-mode exit 1 is a tooling
defect ("it can only pass once, right after its own append"). Its strongest failure, verbatim: "**the memo's
own headline nights bar (148.9m, 'Bloomberg MODL, 12 Sep, 28 estimates') does not reproduce from that
screenshot's own transcription (149.0m)**" — resolved for the model by DEC-0005 at 149.0, unresolved in
memo v3.

### 7.4 The open items on this line, in one list

1. **Memo wording on the index's validation status.** Memo v3's bare "0.68x naive" is what the SR note
   forbids. DEC-0004 adopts the three-ratio sentence; the memo has not been changed yet.
2. **Whether the memo says out loud that 146.3m is a bias correction.** D1's recommendation is yes, one
   clause, because leaving it out invites the judge question with no good answer. Not yet done.
3. **The 3Q26 → 4Q26 carry (β).** Base carries no carry; the adopted object's own β is 0.5, which would put
   4Q26 at 7.93% / 131.6m.
4. **D-11 / the 1Q27 construction**: bridge 169.02 vs ledger schedule 167.1, plus the 2Q27 ordering inversion
   that has to be resolved before the descriptive rows are used — **and the fact that the adopted 1Q27 base
   (169.0178m / +8.206%) sits on the pre-registered 11 February threshold that falsifies the RNPL module
   (≥ +8.2%, 169.0m).**
5. **Re-run `h1_to_h2_bridge_v3.py` and `06_fy27_path_v2` on the adopted 146.3m base**, so the FY26
   denominator and the pass-line exit checks use the governing number. Cross-lane request, 0.7 seconds.
6. **Correct `D1_prereg_thresholds.csv`'s "0.9 to 1.8 points" lap range to 0.70–0.88**, by dated correction
   note rather than an edit to another lane's artefact.
7. **Correct `LINES.md`'s attribution** of FY27 nights +6.4% to `ALPHA_F_RNPL.md`.
8. **Stop quoting +17.9% / +16.5% next to a nights number** — they are revenue comps; the nights comps are
   +9.2% and +10.3%.

---

## 8. Provenance table

Every number in this file, with its file path, the cell or row it comes from, its receipt, and its decision.
Paths are relative to `/Users/theomachado/Citadel-ABNB`.

| # | number | file path | cell / row | receipt | decision |
|---|---|---|---|---|---|
| 1 | nights 1Q23–2Q26 (121.1 … 148.3) | `data/processed/abnb_driver_history_quarterly.csv`; `data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv`; `data/processed/airbnb_quarterly_kpis.csv`; `data/processed/abnb_edgar_quarterly_kpis.csv` | `nights_m` by (year, q); H0 §2 rows `actual / <q> / nights_m` | `data/processed/pitch_model_v2/receipts/H0/receipt.json` (exit 0, GAAP layer); panel attempt `receipt_panel_attempt.json` (exit 1) | DEC-0003 |
| 2 | XBRL endpoint | `analysis/src/abnb_costlines_from_xbrl.py` | `https://data.sec.gov/api/xbrl/companyfacts/CIK0001559720.json`; Q4 = FY − 9M | same, max abs diff 0.0, wall 0.4s | DEC-0003 |
| 3 | nights agree exactly across five files | H0 §4 row 1; H0 §6 row 3 | "max abs diff 0.0 (exact)", 14 × 12 line items | H0 receipt | DEC-0003 |
| 4 | basis choices (G&A ex-lodging; SBC $290M/$411M; shares 640.0m/614.0m) | `02_financial_panel/02_reconciliation.csv` | lines `sbc_total_is`, `shares_diluted_m`; `ga_cash_ex_lodging` | H0 §4 | DEC-0003 |
| 5 | GBV identity 0.270% (4Q24, 17,552.43 vs 17,600) | `data/processed/pitch_model_v2/receipts/D6/d6_history_identity.csv`; `05_backtests/B1_TAKE_RATE_RECONCILIATION.md` §3 | max \|dev\| row | `receipts/D6/` (match yes) | — |
| 6 | 363 dumps / 123 markets / reviews to 17 Aug 2026 | `docs/q3nowcast/SYNTHESIS.md` | §2 row E, data column | D1 §3 step 1 | DEC-0004 |
| 7 | 697,888 rows counted layer | `data/processed/q3nowcast/E/market_vintage_daily.csv` | row count | D1 §3 step 2 | DEC-0004 |
| 8 | region weights 28.3 / 41.6 / 17.9 / 12.3 | `analysis/src/q3nowcast/E4_build_index.py` | `FY25_NIGHTS_SHARE` | — | — |
| 9 | survivorship 15–16% per year of dump age; wedge 20.7 vs 20.4pp | `docs/q3nowcast/SYNTHESIS.md` §2 row E; `analysis/src/q3nowcast/E4_build_index.py` `wedges()` → `survivorship_wedge.csv`; `E7_report.py` `annual_attrition_pct` | status column | D1 §3 | DEC-0004 |
| 10 | 364-day matched window, *k*-day truncation rule | `analysis/src/q3nowcast/E6_nowcast.py` | `WEEK_SHIFT = 364`; docstring points 1–3 | — | — |
| 11 | raw index read **+10.041046%**, slope 0.322138, intercept 1.525819, r 0.861819, band 8.564–11.518 | `data/processed/q3nowcast/E/q3_2026_nowcast.csv` | row (`yoy_all`, `w_reviews`, `GLOBAL`), cols `implied_nights_yoy`, `slope`, `intercept`, `r`, `lo`, `hi` | `receipts/D1/receipt.json`, `receipt_E6.json` (exit 0) | DEC-0004 |
| 12 | partial index 26.3462 → full 26.4335 (gap +0.0872) | same file | cols `partial_index_3q26_pct`, `gap_mean_pp`, `full_index_3q26_pct` | same | — |
| 13 | W2 ratio **0.683209**, W1 ratio **0.837125** | `data/processed/q3nowcast/E/backtest_abnb_quarterly.csv`; recomputed from `backtest_wf_paths.csv` | feature `GLOBAL\|yoy_all\|w_reviews`, lag 0, level, target `nights_yoy`, windows `2023Q1+` / `2022Q1+` | `receipt_E5.json` (exit 0); jackknife 0.6276–0.8598 | DEC-0004 |
| 14 | W2 bias **+0.518452pp** (n 10), W1 bias **+1.631798pp** (n 14) | `data/processed/q3nowcast/E/backtest_wf_paths.csv` | mean `err_feature` by window | `receipts/D1/d1_recompute.py` | DEC-0004 |
| 15 | **9.522594% → 146.32m** (committed 146.3m) | `receipts/D1/d1_recompute.py`; base 133.6m from `abnb_driver_history_quarterly.csv` (2025 q3) | derived | `receipts/D1/receipt.json`, \|Δ\| 0.02m, tolerance ±0.1m | DEC-0004, DEC-0024 |
| 16 | W1-corrected **8.409248% → 144.8m** | same arithmetic with the W1 bias | derived | D1 §6 strongest failure | — |
| 17 | re-vintaged ratios **0.683 / 0.841 / 0.757 / 0.713** | `data/processed/q3nowcast_v2/E/t1_fail_e5_rerun.csv`; `analysis/src/q3nowcast_v2/E/V6_backtest_substituted.py` | four variants | `receipt_V6.json` (exit 0, byte-identical) | DEC-0004 |
| 18 | T1 −10.0pp (+90.4 vs +80.5), regions −6.6 to −15.4pp, n 114 / 1,357; T2 0.660 (n 1,246); T3 −65.8% | `docs/revenue-forecast-strategy/05_backtests/WPK_reviews-index-2023-vintage.md` | Verdict §; §0 pre-registration | inherited (raw 2023 mirror not on this machine) | DEC-0004 |
| 19 | "Do not present the old 0.68x result as a current two-window validated forecast" | `05_backtests/SR_QUARTER_SUBMISSION_READINESS_v1.md` | governing instruction | — | DEC-0004 |
| 20 | adopted object **N(9.5, 1.70)**, P(≥147.0m) 0.386, P(≥147.8m) 0.260, `centre_source` "bias-corrected 9.52" | `docs/pitch-forecasts/questions/risk-q3-nights-meets-guide/datasets/adopted_print_states_v2.json` | A09 rev 2 | — | DEC-0004 |
| 21 | module 3Q26 **+9.49% / 146.3m**; M1 +0.304, M2 −0.113, M3 −0.019, M4 −0.568 | `data/processed/rnpl_short_audit/rnpl_nights_module.csv` | row (base, 3Q26) | `receipts/D2/` side receipts | DEC-0004 |
| 22 | bridge pattern-only **+9.49% / 146.3m** | `data/processed/nights_baseline_reconciliation.csv`; `data/processed/h2_bridge_v3/h2_bridge_v3_rebased_lines.csv` | row "H1-H2 bridge, pattern only"; col `pattern_only` = 9.491667 | `receipts/D3/receipt.json` | DEC-0004 |
| 23 | external stack **12 series, median +9.2324%, range 6.753–11.961 → 145.9m** | `data/processed/q3nowcast/G/G_nowcast_3q26_observable.csv`; `analysis/src/q3nowcast/G2_external_backtests.py` | rows with `target = nights_m_yoy_pct` | `receipt_G2.json` (exit 0) | DEC-0004 |
| 24 | hotel RevPAR 0.665 (W2) / 0.755 (W1); NTTO 0.743 / 0.903 | D1 §6 test record; `G_nowcast_3q26_observable.csv` `wf_ratio_vs_naive` | — | `receipt_G2.json` | — |
| 25 | team baseline **+9.89% / 146.8m**, fitted RNPL +2.40 and fee+cancel +2.29 NA points | `data/processed/nights_baseline_reconciliation.csv` | row "PR #32 NA-lap model, base" | inherited (`origin/krish/nights-quarterly`) | DEC-0004 (rejected) |
| 26 | "the team baseline is a bridge, not a scored object"; 5bp of take rate | `05_backtests/PREREG_ABNB-INT-v1.md` | D-02 | — | DEC-0004 |
| 27 | Street 3Q26 **149.0m** (low 147.0 / high 151.0, n 28, MODL 12 Sep) | V1 §2a `street_nights_m` row; `E_positioning_card.py` | — | licensed aggregate, not in repo as raw | DEC-0005 |
| 28 | memo v3's 148.9m traced to a 4 Sep "Bloomberg FA" capture | `docs/pitch-model-v2/dossiers/V1_v1_street.md` | §2 nights row, §4, §7 item 1 | `receipts/V1/` (`consensus_stamp_v2` exit 1, tooling defect) | DEC-0005, DEC-0012 |
| 29 | guide "low double digits"; ≥10.0% → 147.0m mapping is ours | 2Q26 shareholder letter via `data/processed/overnight/02_guidance_ledger.csv`; `nights_baseline_reconciliation.csv` last row | — | — | — |
| 30 | no Street nights baseline in the harness (19 `nights` rows `role=at_print`, `vendor_not_recorded`) | `05_backtests/PREREG_ABNB-INT-v1.md` | INT-02 | — | — |
| 31 | 4Q26 base **+8.12% / 131.8m**, band 8.0 / 8.86 | `data/processed/h2_bridge_v3/h2_bridge_v3_rebased_lines.csv` | row (4Q26, `nights_yoy_pct`): `adopted` 8.12, `adopted_mm` 131.8, `band_lo` 8.0, `band_hi` 8.86 | `receipts/D2/receipt.json` (6 checks, all pass) | DEC-0019 |
| 32 | lap 0.70 @ 40% / **0.78 @ 45%** / 0.88 @ 50%; 70% and 100% ruled out | `data/processed/overnight2/D/D1_exna_4q26_gap.csv` | `pts_missing_from_4q26`, `consistent_with_4q25_disclosure` | `receipt_D1_cohort.json` (max abs diff 0.0, all 8 CSVs) | DEC-0019 |
| 33 | "over 200 basis points … roughly 300 basis points … in Q4" (4Q25) | `data/processed/overnight2/D/rnpl_statement_ledger.csv` | row **D014**, `official_or_mirror = mirror` | `analysis/src/overnight2/D0_rnpl_statement_ledger.py` | DEC-0019 |
| 34 | "approximately three points … approximately four points … in Q1" (1Q26) | same ledger | row **D032** | same | — |
| 35 | Oct–Dec 2025 dates, global scope; PMS hosts from Oct, remaining from Dec | `data/raw/letters/3Q25_d40503dex991.htm`, `4Q25_d58192dex991.htm` via the ledger | rows **D012, D013, D024, D060**, `official` | same | DEC-0019 |
| 36 | 4Q25 out-of-sample check: 40% → 2.05pt, 50% → 2.23pt pass; 70% → 2.58, 100% → 3.10 fail | `data/processed/overnight2/D/D1_bundle_crosscheck.csv`; D2 §6 | — | `receipt_D1_cohort.json` | DEC-0019 |
| 37 | case A **132.7m / +8.86%** (PR #32 quotes 8.9) | `nights_baseline_reconciliation.csv` row "PR #32 NA-lap model, base", `q4_nights_mm` | — | — | DEC-0019 (band top) |
| 38 | 4Q26 exit re-derived at **8.157** vs adopted 8.12 ("rounding of 132.7/121.9") | `data/processed/margin_build/06_fy27_path_v2/06_pass_line.csv` | test 6 | `receipts/D3/receipt.json` | — |
| 39 | `rnpl_v2` registered paths: `exna` 131.7739, `theo` 131.1644, `team` 132.7491 | `data/processed/forecast_methods/rnpl_v2/live_scenarios.csv` | `q4_nights_m` | `receipt_rnpl_v2.json` (exit 0, byte-identical) | DEC-0019 |
| 40 | module 4Q26 **+7.61% / 131.2m**; M1 −0.590, M2 −0.156, M3 −0.095, M4 −0.446 | `data/processed/rnpl_short_audit/rnpl_nights_module.csv` | row (base, 4Q26) | — | DEC-0019 (short, not base) |
| 41 | `cancel_drag_pp, base, 4Q26 = 0.00` | D2 §2a | model-inputs table | — | DEC-0019 |
| 42 | cohort drag central cells −0.14 / −0.28 / −0.57 / −0.85; full grid −1.36 to −0.08 | `data/processed/overnight2/D/D1_cohort_matrix_cancellation.csv`, `D1_rnpl_cohort_scenarios.csv` (2,025 cells) | stdout of `D1_rnpl_cohort_scenarios.py` | `receipt_D1_cohort.json` | — |
| 43 | adopted Q4 object: mean 8.61, sd 2.28, P(≥134.0m) 0.307, P(≤131.0m) 0.3089, P10 5.56 / P90 11.44; `q4 = 8.1 + 0.5(Q3 − 9.5)` | `docs/pitch-forecasts/questions/risk-q4-nights-print-meets-street/datasets/adopted_q4_states_v2.json` | A12 rev 2 | — | DEC-0019 |
| 44 | β = 0.5 carry → **7.93% / 131.6m**; β = 1.0 → 7.73% / 131.3m | D2 §7 conflict 2, §8 choice 2 | derived | — | open |
| 45 | Street 4Q26 **134.0m, +9.93%** | V1 §2a `street_nights_m` 4Q26; D2 §2 | MODL 12 Sep, n 28 | — | DEC-0018 (used in take rate) |
| 46 | case A vs case B ≈ **$21M** of revenue at ADR $173.55 | `research/notes/adrv3/N_fx-estimator-and-q4-lap-decisions.md` memo 2; D2 §7 | — | — | — |
| 47 | `D1_prereg_thresholds.csv` says the lap is "0.9 to 1.8 points" (contradicts 0.70–0.88) | `data/processed/overnight2/D/D1_prereg_thresholds.csv` | 4Q26-guide row | same run as #32 | open (D2 §8 choice 5) |
| 48 | 2027 build: NA 2.31 @ 0.291/0.288/0.282; ex-NA 10.773 / 10.452 / 10.131 / 9.810; lap −0.742; RNPL −0.363 / −0.907; events +1.0 / −0.5 | `data/processed/margin_build/06_fy27_path_v2/06_nights_build.csv` | four base rows | `receipts/D3/receipt.json` (byte-identical) | DEC-0025 |
| 49 | NA +2.31% for 2027 | `data/processed/na_nights_lap_scenarios.csv`; `analysis/src/na_nights_reconciliation.py` | row "base: no product lever", col 2027 = 0.0231 | not re-run in D2 (outside package list) | DEC-0025 |
| 50 | 1Q27 RNPL phase fraction **0.4**, "Fraction is judgement"; `exna_phasing_rule` judgement; 55 rows / 10 judgement | `data/processed/margin_build/06_fy27_path_v2/06_assumptions.csv` | `exna_rnpl_lap_fraction_1Q27`, `exna_phasing_rule`, `is_judgement` | `receipts/D3/` | DEC-0025 |
| 51 | 2027 levels **169.0178 / 157.1001 / 155.958 / 139.7655**; y/y 8.206 / 5.934 / 6.229 / 6.045 | `data/processed/margin_build/06_fy27_path_v2/06_revenue_path_3q26_4q27_v2b.csv` | rows `<q>,base,nights_mm` and `nights_yoy_pct` | `receipts/D3/receipt.json` | DEC-0025 |
| 52 | FY27 **621.8414m / +6.642%**; FY26 **583.1113m** | `data/processed/margin_build/06_fy27_path_v2/06_annual_fy26_fy28_v2b.csv` | rows (FY27, base) and (FY26, base), col `nights_mm`, `nights_mm_yoy_pct` | `receipts/D3/receipt.json`, exact match | DEC-0025 |
| 53 | 3Q26 in the FY26 denominator is still **146.813m** | same v2b file | row `3Q26,base,nights_mm` | `receipts/D3/` | open (D3 §7 conflict 1) |
| 54 | FY27 on the adopted 146.3m base = **+6.73%** (FY26 582.62m) | arithmetic done in this file on rows #51–#53 | derived here | — | open |
| 55 | D2's descriptive 1Q27 **167.1 / +6.97%**, 2Q27 **157.8 / +6.42%** | D2 §2a | descriptive rows on the `exna_lap = False` reference 8.17 | `receipts/D2/` | DEC-0025 (D-11 open) |
| 56 | PR #32 flat **−1.75** from 1Q27, nothing in 4Q26 → ~0.8pp double count | D2 §7 conflict 5 (D-11); AGENT_BRIEF §3 D-11 | — | — | open |
| 57 | `alt_rnpl` FY27 **+6.42%** (621.6mm on 584.1mm) | `data/processed/margin_build/06_fy27_path_v2/06_pr32_rederivation.csv` | row "PR32 total base FY27 nights level, exna_lap=True" | `receipts/D3/` byte-identical | DEC-0025 (alternative) |
| 58 | corroborations +6.42% / +6.52% / module +6.41% | `docs/rnpl-short-audit/02_fy27-decomposition-rnpl-synergy.md`; `rnpl_nights_module.csv` | — | — | — |
| 59 | `LINES.md` mis-attributes FY27 +6.4% to `ALPHA_F_RNPL.md` | `docs/pitch-model-v2/LINES.md` line 98 | — | D3 §2a note | open |
| 60 | flip sensitivity FY27 **+8.17%**, revenue $15,964M / +11.9%, +$167M / +1.2pp | `docs/margin-build/notes/06v_fy27_path_check.md` lines 62, 78, 159; `06_nights_build.csv` col `sens_no_exna_lap_case_A_pct` | `base_no_exna_lap_2027` | read-only (out of D3's packages) | DEC-0025 (alternative) |
| 61 | independent second build FY27 **+6.56% / 621.4mm**, 0.08pp gap | `docs/margin-build/notes/06v_fy27_path_check.md`; `data/processed/margin_build/06v_fy27_path_check/` | — | read-only | — |
| 62 | 7/7 internal pass line | `data/processed/margin_build/06_fy27_path_v2/06_pass_line.csv` | all rows | `receipts/D3/` | — |
| 63 | B3 FY27 volume **+9.4558%**, no lap | `05_backtests/B3_FY27_DECOMPOSITION.md` | line 51 / row COMPUTED_GBV | — | — |
| 64 | eligibility dates UK 18 Feb, APAC/Australia 23 Feb, Canada 4 Mar; BRL/INR/TRY excluded | `docs/overnight2/SYNTHESIS.md` §1 row "International RNPL rollout" | — | — | — |
| 65 | July 2026 booking-type expansion, unnamed and unsized; carried at +0.1 to +0.3pt (assumed) | ledger row **D044**; D2 §9 Q6 | — | — | — |
| 66 | 46–49% of excess cancellations from earlier cohorts | `docs/overnight2/SYNTHESIS.md` §2 D | — | — | — |
| 67 | 17–28M unpaid nights at 30 June (7–19M withdrawn) | `research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md` STATUS header; `docs/rnpl-short-audit/04_balance-sheet-verification.md` | bottom line 3, MODIFIED | `analysis/src/rnpl_short_audit/verify_balance_sheet.py` | — |
| 68 | 2Q26 10-Q: RNPL bookings "have experienced higher cancellation rates" | `data/raw/regulatory/quantification/abnb_2026q2_10q.html`, MD&A Key Business Metrics | CONFIRMED verbatim | verification note | — |
| 69 | 5 Nov RNPL tells (bundle ≤1.5 / ≥2.5; share flat-or-down / ≥25%; unearned fees ≤−3% / ≥+6%) | `data/processed/overnight2/D/D1_prereg_thresholds.csv`; `research/notes/overnight2/D_*.md` §5 | — | — | — |
| 70 | corrected unearned-fees rule: (UF y/y − GBV y/y) ≤ −18 supports, −12 to −18 in line, > −8 weakens | `research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md` STATUS header | bottom line 2 REFUTED | verification note | — |
| 71 | 34-market calendar study: **+2.06pp, permutation p 0.26**, bootstrap 0.69–3.47 (2,000 reps), 32 markets (25 non-US / 7 US), collapses on one 29-listing market, Australia-driven | `docs/overnight2/SYNTHESIS.md` §2 A; D2 §6 | — | — | — |
| 72 | calendar booking pace **r = −0.43** (sign inverted), retired | `analysis/src/q3nowcast/F*.py`; `docs/q3nowcast/SYNTHESIS.md` §2 row F; D1 §4 last row | — | — | — |
| 73 | World Cup: unsized by management; no lift to 3Q26 booked nights; 2Q27 lap **−0.5pt** base | `deck/drafts/memo_v3_short_2026-09-17.md`; `nights_baseline_reconciliation.csv` row 1 note; `06_nights_build.csv` col `event_pts` | — | `receipts/D3/` | DEC-0025 |
| 74 | bridge v1/v2 World Cup +0.5 overlay retired (pts = 0) | `analysis/src/h1_to_h2_bridge_v3.py` docstring, v3 changes | — | `receipts/D3/` | — |
| 75 | FX does not enter nights; FX→mix elasticity ~0.11pp, nets to zero at spot (n 28, perm p 0.04) | `docs/overnight2/SYNTHESIS.md` §2 B; D3 §3 step 2 | — | — | DEC-0010 (FX is a revenue/ADR line) |
| 76 | fee tranche 2 carried at **0.0 points of nights** | D2 §7 near-miss check (ii), on PR #32's fee-elasticity work | — | — | — |
| 77 | ADR fee-migration term K = +0.17pp, sensitivity only | `docs/pitch-model-v2/dossiers/D4_d4_adr.md`; DECISIONS | — | — | DEC-0008 |
| 78 | Strict-to-Firm 2Q26 migration carried by no team model (assumed zero here) | `research/notes/overnight2/D_*.md` §5 "Other next evidence" item 4 (ledger D048) | — | — | open |
| 79 | INT-02 thresholds: ≤8.5% supports, ≥10.3% weakens, 8.6–10.2 inconclusive; band 8.5–11.0; naive +10.34% | `05_backtests/PREREG_ABNB-INT-v1.md` | INT-02 | — | DEC-0004 |
| 80 | band conflict 8.5–10.0 / 8.5–11.0 / 7.3–11.7 resolved | memo v3; PREREG INT-02; `adopted_print_states_v2.json` | — | — | DEC-0004 |
| 81 | 4Q26 guide thresholds ≤7.5 / ≥9.5 / 7.6–9.4 inconclusive; 1Q27 ≥+8.2% falsifies | `data/processed/overnight2/D/D1_prereg_thresholds.csv`; D2 §6 | — | — | — |
| 82 | update rule: centre 9.0 → 0.28, 9.5 → 0.39, 9.9 → 0.48, 10.0 → 0.50 | D1 §8 choice 5, §9 Q5; `adopted_print_states_v2.json` | — | — | DEC-0004 |
| 83 | +17.9% / +16.5% are **revenue** comps; nights comps are +9.2% / +10.3% | `docs/rnpl-short-audit/02_fy27-decomposition-rnpl-synergy.md` §3 ("FY26 comp (revenue)"); `05_quality-of-growth-study.md` table | — | — | correction stated here |
| 84 | grades: H0 B, D1 B, D2 B, D3 B, V1 dossier C → B | each dossier §10; DEC-0003, DEC-0012 | — | — | DEC-0003, DEC-0012 |
| 85 | adopted 1Q27 base **169.0178m / +8.206%** sits on the pre-registered module falsifier **≥ +8.2% / 169.0m** | `06_revenue_path_3q26_4q27_v2b.csv` rows `1Q27,base,nights_mm` and `nights_yoy_pct`; D2 §2a breaker rows and §6 last row | comparison made in this file | `receipts/D3/`, `receipts/D2/` | open — flagged here, not resolved |
| 86 | 2Q27 step −2.272pt decomposes to −0.544 (RNPL phase) + −1.500 (event swing) + −0.227 (ex-NA contribution) | `06_nights_build.csv`, 1Q27 and 2Q27 base rows | arithmetic done in this file | `receipts/D3/` | — |
| 87 | historical y/y 1Q24–2Q26 (+9.50 … +10.34) | computed in this file from the printed levels in row #1 | derived | — | DEC-0003 |
