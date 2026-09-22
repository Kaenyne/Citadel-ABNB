# Nights line, version 2 — design

**What this file is.** The construction of the nights line after **DEC-0028** (18 Sep 2026), which retired
the "14-point regression of printed nights on a review index" as the *spine* of the nights thesis and moved
the line to a **disclosed-mechanism** build, with the alt-data reads demoted to a **constellation of
cross-checks**. It supersedes parts of `docs/pitch-model-v2/lines/final_nights.md` — §9 says exactly which
parts — and it is the design document the model's named inputs are taken from.

**Scope and rules.** Base scenario only (**DEC-0020**). No input was chosen to match a price, a target or a
priced downside (**DEC-0016**). **No new regressions** were run: the ~3,500-test record of 6–7 Sep stands and
is respected — nothing on the nights level beats a naive baseline on both windows except hotel RevPAR (0.68
W2), BEA hotels (0.71) and the reviews index (0.68 W2 / 0.84 W1 / 0.76 re-vintaged), and none of those three
is the spine here. Every number below is from a file in this repository, a filing, or an explicitly labelled
assumption. Where two files disagree, both are shown and the governing one is named.

**Branch** `theo/pitch-model-v2`, HEAD `bf13b2d`. **Web fetches: zero** (none were needed; the FY2025 10-K
regional table is in the repo at `data/raw/regulatory/quantification/abnb_2025_10k.json`, and every letter
sentence quoted here is carried verbatim in a processed mirror that names its SEC source file and URL).
**Receipts:** `data/processed/pitch_model_v2/receipts/N2/`. **Chart data:**
`docs/pitch-model-v2/lines/figures/nights_constellation_3q26.csv`.

**Reproductions run for this file** (all exit 0, all byte-identical to the committed outputs):

| what | command | result |
|---|---|---|
| PR #32 nights build | `PYTHONPATH=analysis/src python3 analysis/src/pitch_model_v2/repro.py --id N2 --watch data/processed/nights_quarterly_total.csv --watch data/processed/nights_quarterly_na.csv --cmd "python3 analysis/src/nights_quarterly.py"` | exit 0, 0.2 s, `changed: []`, `new_files: []`, tree restored. Receipt `receipts/N2/receipt_nights_quarterly.json`, stdout `stdout_nights_quarterly.txt` |
| NA reconciliation | same wrapper, `--id N2_na`, watching `na_nights_lap_scenarios.csv`, `na_nights_decomposition.csv`, `na_nights_step_history.csv`, `na_nights_reconciliation.csv`, `--cmd "python3 analysis/src/na_nights_reconciliation.py"` | exit 0, 3.2 s, `changed: []`. Receipt `receipt_na_nights_reconciliation.json` |
| this file's own mechanism and band | `PYTHONPATH=analysis/src python3 data/processed/pitch_model_v2/receipts/N2/n2_mechanism.py` (wrapped, `--id N2_mech`) | exit 0, 0.3 s. Outputs `n2_mechanism_quarterly.csv`, `n2_band.csv`, `figures/nights_constellation_3q26.csv`. Receipt `receipt_n2_mechanism.json` |

Both `.venv-pd2` and plain `python3` (pandas 3.0.0) run these; pandas 3 did not break either script, so the
fallback interpreter was not needed. `analysis/src/nights_quarterly.py` imports `choice_nights_driver`, which
is present; no input was missing.

---

## 1. The claim, in one paragraph

Airbnb's nights growth from 4Q26 through 2Q27 is mostly **arithmetic on the company's own disclosures**, not a
forecast. Management launched three products on dated anniversaries — Reserve Now, Pay Later in the US in
August 2025, a global cancellation redesign announced in October 2025, and the migration of hosts to a single
15.5% fee from October–December 2025 — and told us twice what they were worth: "over 200 basis points of
growth in nights booked" in 4Q25 and "approximately three points" in 1Q26. A level gain that went live on a
known date lifts year-over-year growth for exactly four quarters and then stops lifting it, **whatever demand
does**. The US leg laps in 3Q26, the global cancellation and fee legs lap in 4Q26, and the international
Reserve Now, Pay Later leg laps through 1Q27 and 2Q27. Put those dated anniversaries on the company's own
regional growth disclosures and the path is **+9.9% in 3Q26, +8.1% in 4Q26, +8.2% in 1Q27 and +5.9% in 2Q27**
— a two-and-a-half point deceleration in three quarters that needs no view on travel demand at all. The 3Q26
print itself we hold as a **range, not a point**: the mechanism says 146.8m, an independent stays index says
146.3–147.0m, an external macro stack says 145.9m, and our honest walk-forward error on any of them is
1.5–2.4 points, so the print is 144–149m. The Street's 149.0m bar is a different kind of object: it requires
nights to **accelerate** to +11.5% in the quarter the US product leg laps, which on the same identity means
North America must go from +8% to **+11.3%**, or the rest of the world from +12.8% to **+13.9%**. That is the
variant view — not that travel is weak, but that the Street is extrapolating a growth rate whose sources
carry expiry dates the company has already published.

---

## 2. The mechanism, quarter by quarter, 3Q25 through 4Q27

### 2.0 The identity the whole line runs on

One equation, applied to every quarter:

```
total nights y/y  =  s · NA_yoy  +  (1 − s) · exNA_yoy  +  lap terms  +  event terms
```

where `s` is the **prior-year** North America share of nights (the correct y/y weight), `NA_yoy` is North
America's growth, `exNA_yoy` is the nights-weighted growth of EMEA + Latin America + Asia Pacific, and the lap
and event terms are expressed in points of **total** nights. Nothing in this identity is fitted. What is
fitted — two parameters, named and bounded in §2.1 — is the split of the NA product bundle into its RNPL leg
and its fee-plus-cancellation leg.

**Where each input comes from.** Airbnb discloses regional nights **annually and exactly** in the 10-K
"Geographic Mix" table (FY2025: North America 158m / 30%, EMEA 215m / 40%, Latin America 90m / 17%, Asia
Pacific 70m / 13%, total 533m, +8%; `data/raw/regulatory/quantification/abnb_2025_10k.json` index 43,
transcribed to `data/processed/adr/01_regional_annual.csv`). It does **not** disclose regional nights
quarterly. What it gives quarterly is a **four-region paragraph in every shareholder letter with a bucket
phrase** — "mid-single digit growth", "high-single digit growth", "approximately 20% growth". WS10
(`research/notes/overnight/10_regional-and-segment-decomposition.md`) maps those phrases to ranges
(low-single 1–3, mid-single 4–6, high-single 7–9, low-double 10–12, mid-teens 14–16, high-teens 17–19,
low-20s 20–23), takes the midpoint, and keeps the raw phrase. **That mapping is the load-bearing assumption of
this whole line** and WS10 says so: "Bucket midpoints are the load-bearing assumption. The reconciliation
residual (±1.1pp, mean −0.41pp over the last four quarters) is the honest error bar on the whole regional
layer."

### 2.1 The values

Levels are in millions of Nights and Seats Booked; growth rates in per cent; bundle and lap legs in **points
of total nights** unless a column says otherwise.

| period | NA share s | NA underlying y/y | NA bundle (pts of NA) | ex-NA underlying y/y | ex-NA bundle live (pts of total) | fee/cancel lap | RNPL lap | event | calibration residual | total y/y | level (m) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 3Q25 | 0.307 | +2.60 | +2.40 | +10.49 | 0.00 | — | — | — | −0.01 | **+8.795** | **133.6** |
| 4Q25 | 0.300 | +2.60 | +2.40 | +11.60 | +0.79 | — | — | — | +0.20 | **+9.820** | **121.9** |
| 1Q26 | 0.293 | +3.31 | +4.69 | +10.70 | +1.65 | — | — | ME −1.0 | −0.76 | **+9.154** | **156.2** |
| 2Q26 | 0.293 | +3.31 | +4.69 | +12.81 | +1.65 | — | — | WC unsized | −1.06 | **+10.342** | **148.3** |
| **3Q26** | 0.288 | +3.31 | **+2.29** | +11.621 | +1.65 | 0.00 | 0.00 (US leg lapped in full) | 0.0 | in WS10 total | **+9.89** | **146.8** |
| **4Q26** | 0.282 | +3.31 | 0.00 | +11.095 | +0.91 | **−0.742** | 0.00 | 0.0 | in WS10 total | **+8.16** (DEC-0019 8.12) | **131.8** |
| **1Q27** | 0.291 | +2.31 | 0.00 | +10.773 | +0.54 | **−0.742** | **−0.363** | **+1.0** ME lap | in WS10 rate | **+8.206** | **169.02** |
| **2Q27** | 0.291 | +2.31 | 0.00 | +10.452 | 0.00 | **−0.742** | **−0.907** | **−0.5** WC lap | in WS10 rate | **+5.934** | **157.10** |
| **3Q27** | 0.288 | +2.31 | 0.00 | +10.131 | 0.00 | **−0.742** | **−0.907** | 0.0 | in WS10 rate | **+6.229** | **155.96** |
| **4Q27** | 0.282 | +2.31 | 0.00 | +9.810 | 0.00 | **−0.742** | **−0.907** | 0.0 | in WS10 rate | **+6.045** | **139.77** |
| **FY26** | — | — | — | — | — | — | — | — | — | +9.40 | **583.11** |
| **FY27** | — | — | — | — | — | — | — | — | — | **+6.642** | **621.84** |

The same table, cell by cell, with the source tag for every number:

| period | NA share s | NA underlying | NA bundle | ex-NA underlying | ex-NA bundle | fee/cancel lap | RNPL lap | event | total / level |
|---|---|---|---|---|---|---|---|---|---|
| 3Q25 | WS10 estimate `10_regional_panel_quarterly.csv` `na_nights_share_est_pct` (not disclosed) | **filing**: FY25 10-K 158/154 = +2.6% | **fitted in PR #32 on 3Q25 alone** (5.0 − 2.6) | WS10 share-weighted buckets, `ex_na_nights_yoy_est_pct` | zero: ex-NA RNPL not launched (ledger D023, D025) | n/a | n/a | n/a | **printed**, 8-K Ex-99.1 KPI box / 10-Q |
| 4Q25 | WS10 estimate | carried from FY25 | fitted, carried | WS10 buckets | 0.45 × 1.752 = 0.79, **assumed split** inside management's ">200bp" (D014) | n/a | n/a | n/a | **printed** |
| 1Q26 | WS10 estimate | choice model `na_nights_lap_scenarios.csv` 2026 = 3.31 | **fitted in PR #32 on 1Q26** ((8.0 − 3.31) − 2.40) | WS10 buckets | 3.0 − 0.288 × 4.69 = 1.649, from **call D032** "approximately three points" | n/a | n/a | **filing** 1Q26 letter: "approximately 10% absent the conflict" → ~100bp | **printed** |
| 2Q26 | WS10 estimate | choice model | fitted, carried | WS10 buckets | carried; **management gave no figure in 2Q26** (D045) | n/a | n/a | World Cup, **never sized by management** (8 event discussions, `r15_v2_event_record.csv`) | **printed** |
| 3Q26 | WS10 estimate 28.8 | choice model 2026 | fitted; **RNPL leg removed in full** — assumed: full US lap | WS10 forecast TOTAL less NA at WS10's own share | still live | **assumed zero**: legs lap from 4Q26 (ledger D012, D013, D024, D060) | **assumed full**: "beginning of Q3" reading of D008 | assumed zero (2Q26 call: "In Q3, we are not assuming any significant impact… Middle East") | mechanism |
| 4Q26 | WS10 estimate 28.2 | choice model 2026 | zero: whole NA bundle lapped | WS10 forecast 4Q26 | fee/cancel leg removed | **0.45 × 1.649**, split **assumed** inside 40–50% pinned by D014 | ex-NA RNPL still in window (live 17 Feb–4 Mar 2026) | zero | mechanism; DEC-0019 |
| 1Q27 | 0.291, **assumed** chain of the FY25 10-K 29.6% with 1H26 growth (`06_assumptions.csv` `is_judgement = True`) | choice model 2027 = 2.31 | zero | WS10 FY27 rate **phased linearly**, `exna_phasing_rule`, judgement | — | carried flat, **not re-applied** | **0.40 phase-in, assumed** (`exna_rnpl_lap_fraction_1Q27`, judgement) | **+1.0**, laps the ~100bp Middle East headwind management sized in the 1Q26 letter | 06 build; DEC-0025 |
| 2Q27 | 0.291, assumed | choice model 2027 | zero | WS10 phased | — | carried flat | full | **−0.5, assumed** lap of an unsized World Cup pull-forward (bear −0.75, bull 0) | 06 build |
| 3Q27 | WS10 28.8 | choice model 2027 | zero | WS10 phased | — | carried flat | full | zero; July 2026 expansion laps here, carried at zero | 06 build |
| 4Q27 | WS10 28.2 | choice model 2027 | zero | WS10 phased | — | carried flat | full | zero | 06 build |

Three properties of that table a judge will test, and the honest answers:

1. **The bucket midpoints do not add up, and we do not hide it.** In 1Q26 the share-weighted regional
   midpoints give +9.91% against a printed +9.15%; in 2Q26 they give +11.40% against +10.34%. The
   `residual_vs_total_pp` column carries −0.76 and −1.06. WS10 folds the mean of the last four quarters,
   **−0.41pp**, into its forward TOTAL rows as a constant calibration, so the forward ex-NA rates used above
   already contain it. WS27 (`research/notes/overnight/27_regional-bucket-check.md`) works out which region is
   at the wrong end of its bucket and finds **North America has sat at the bottom of its bucket in five of the
   last six quarters**, i.e. the 2Q26 NA base is probably **7%, not 8%**. That is the single most likely
   direction of error in the fit, and §4 carries it as a band parameter.
2. **The NA share is an estimate and it disagrees with the 10-K.** WS10's estimated shares (28.8% for 3Q26)
   are built from XBRL regional revenue over a regional ADR index; the FY2025 10-K gives NA at **29.6%**
   (158/533) and prints 30%. WS10's own note says the shares are "estimated, not disclosed, except the ~30%
   North America anchor for 2025 that they are calibrated to". An independent check
   (`research/notes/overnight2/C_consumer-relative-strength-regional-split.md`) re-weights WS10's cells on the
   disclosed 10-K shares and gets 3Q26 10.57% instead of 10.69% and 4Q26 10.17% instead of 10.35% before the
   −0.41pp calibration — so WS10's share error **overstates its own total by 0.12 to 0.18pp**. Governing
   choice: we keep WS10's shares, because the committed model runs on them and because changing them changes
   the calibration constant they were fitted with; we state the 0.12–0.18pp overstatement as a known bias in
   the **upward** direction, which cuts our way.
3. **The FY25 regional nights *shares* constant used by the reviews index is mislabelled.**
   `analysis/src/q3nowcast/E4_build_index.py:45` carries `FY25_NIGHTS_SHARE = {NAM 28.3, EMEA 41.6, LatAm
   17.9, APAC 12.3}` described as "Airbnb FY25 regional nights shares". Those are not the FY25 shares: the
   10-K gives 29.6 / 40.3 / 16.9 / 13.1. The constant is in fact the **2Q26 single-quarter** row of
   `data/processed/adr/04_regional_quarterly_wide.csv`, and the mean of the four FY25 quarters in that same
   file reproduces the 10-K to a tenth. It also sums to 100.1. This affects the **cross-check** (§5), not the
   mechanism; `docs/2026-09-11_q3-nowcast-explainer.md:29` repeats the wrong label and needs a dated
   correction.

### 2.2 3Q26, built from the mechanism, step by step

This is where the team baseline **146.8m / +9.9%** comes from. Nothing about it is a nowcast.

**Step 1 — the pre-product North America run rate.** The FY2025 10-K prints NA nights at 158m against 154m,
which the repo recomputes as **+2.597% ≈ +2.6%** (the 10-K's own printed "% Change" cell says "3 %"; both
levels are rounded to whole millions, so ±0.5m is ±0.45pp of annual growth — an error bar stated in
`03_critiques/C_M4_bottom_up_market_panel.md`). Independently, the choice model
(`analysis/src/choice_nights_driver.py`, run through `na_nights_reconciliation.py`) produces a US nights
growth **with no product lever at all** of **+3.31%** for 2026 and **+2.31%** for 2027
(`data/processed/na_nights_lap_scenarios.csv`, row "base: no product lever"). The point of that agreement,
in the reconciliation note's own words: "the model's pre-product run rate and the pre-RNPL NA run rate are the
same number."

**Step 2 — fit the two product legs on two letter buckets.** `nights_quarterly.py`'s `fit_product()`:

```
RNPL leg          = NA 3Q25 observed (5.0, "mid-single digit growth")  −  2.6 (FY25 10-K)   = +2.40 pts of NA nights
fee+cancel leg    = ( NA 1Q26 observed (8.0, "high-single digit growth")  −  3.31 )  −  2.40 = +2.29 pts of NA nights
peak NA bundle, 1H26                                                                        = +4.69 pts of NA nights
```

3Q25 is the only quarter in which RNPL is live alone in North America, which is why it identifies the RNPL
leg; 1Q26 is the first full quarter with the cancellation redesign and fee tranche 1 ramped, which is why the
step up identifies the rest. **This is the whole fit: two parameters on two bucket midpoints and one annual
10-K anchor.** It is reproduced exactly by this file's receipt and by
`06_fy27_path_v2/run.py` lines 152–159 (`pr32_rnpl_na_pts` 2.40, `pr32_t1_cancel_na_pts` 2.29).

**Step 3 — back out the ex-NA bundle from management's global figure.** Mertz, 1Q26 call (ledger **D032**):
"we estimate these three features delivered approximately three points of nights booked growth and
approximately four points of GBV growth in Q1." Those three points are **global**. With NA contributing
`s × 4.69`, the rest of the world must contribute the remainder:

```
ex-NA bundle (points of total nights) = 3.0 − s × 4.69
   at s = 0.288  →  1.649   (the value the 06 build and this design use)
   at s = 0.291  →  1.635   (the 1Q26 share, arguably the right identification-quarter weight)
   at s = 0.266  →  1.752   (the 2027 share PR #32 used; the value WS-D's 4Q26 gap file used)
```

**Step 4 — put the anniversaries on the calendar.** From `D1_lap_anniversary.csv`, every date from the SEC
letters or the newsroom:

| leg | live from | geography | laps from | source |
|---|---|---|---|---|
| RNPL, US | August 2025 (letter) / "beginning of Q3" (call) | US guests, US domestic stays, flexible or moderate policy | **3Q26** | ledger D001, D004, D008 |
| cancellation redesign | announced October 2025 | **global** | **4Q26** | ledger D012, D060 (both `official`, SEC letters) |
| single fee, tranche 1 | October 2025 PMS hosts, December 2025 most remaining | **global** | **4Q26** | ledger D013, D024 (`official`) |
| RNPL, rest of world | 17 Feb 2026 worldwide; UK 18 Feb, Australia 23 Feb, Canada 4 Mar; BRL/INR/TRY excluded | global ex-NA | **1Q27 partially, 2Q27 fully** | ledger D025–D029, D034 |
| single fee, tranche 2 | announced July 2026, completing during 2026 | global | not before 3Q27 | ledger D047; nights effect carried at **0.0** |
| RNPL, expanded booking types | July 2026 | not specified | 3Q27 | ledger **D044**, unsized |

**Step 5 — assemble 3Q26.** In 3Q26 exactly one leg has lapped, the US RNPL leg, and it is in North America
only. So:

```
NA 3Q26      = 3.31 (underlying)  +  2.29 (fee+cancel still in window)  +  0.00 (RNPL lapped)  =  +5.60%
ex-NA 3Q26   = ( WS10 total 10.29  −  0.288 × WS10 NA 7.00 ) / 0.712                            = +11.621%
total 3Q26   = 0.288 × 5.60  +  0.712 × 11.621  =  1.613 + 8.274                                =  +9.887%
level        = 133.6m × 1.09887                                                                 =  146.81m
```

`nights_quarterly.py` rounds that to **+9.89% / 146.8m**, which is the number the bridge, the 06 FY27 build
and DEC-0028 all carry. Note what the arithmetic is really saying: the mechanism does **not** claim demand is
weakening in 3Q26. It leaves ex-NA growing at 11.6% and takes 1.4 points off North America **because a product
anniversary is inside the quarter**.

The step from 2Q26's printed +10.342% to +9.887% is only **−0.455pp**, and it decomposes into three pieces
that are worth separating because two of them are larger than the step itself:

```
NA contribution      0.293 × 8.00  →  0.288 × 5.60      =  2.344 → 1.613   −0.731pp   (of which the lap is 2.40 × 0.288 = −0.691pp)
ex-NA contribution   0.707 × 12.81 →  0.712 × 11.621    =  9.057 → 8.274   −0.783pp   (WS10's own ex-NA deceleration, a forecast)
calibration residual      −1.059    →       0            (folded into WS10's forward TOTAL at −0.41)  +1.059pp
                                                                            ---------
                                                                            −0.455pp
```

Two honest consequences. First, **the lap is the larger identifiable piece but not the whole step** — an
almost equal amount comes from WS10 forecasting ex-NA growth down 1.2 points, which is a demand assumption,
not arithmetic. Second, **the history rows and the forecast rows are not on an identical basis**: the printed
quarters carry their own reconciliation residual (−0.01, +0.20, −0.76, −1.06) while the forward quarters carry
the four-quarter mean of −0.41 inside WS10's TOTAL. If 2Q26's −1.06 were the right forward constant rather
than −0.41, the WS10 total would be 9.64% instead of 10.29%, ex-NA 10.708% instead of 11.621%, and 3Q26 would
be **+9.24% / 145.9m** — just below the bottom of the §4 envelope. That is the single cleanest way for someone
to argue our number is too high, and we should say it first.

**What the mechanism assumes about the July 2026 expansion.** Nothing — it is carried at **zero**.
`IN_WINDOW["3Q26"]` in `nights_quarterly.py` has no term for it, and `06_assumptions.csv` carries
`rnpl_eligibility_expansion_lap_3Q27_pts = 0.0` with the note "unsized, carried at zero" and
`is_judgement = True`. The only statement on the record is ledger **D044**, a call mirror of 6 Aug 2026:
"Given the strong results that it's delivered, in July, we expanded the types of bookings eligible for Reserve
Now, Pay Later." The booking types are not named and the size is not given. The unified RNPL module carries it
at **+0.1 to +0.3 points** — assumed — and D2 calls it "the largest unquantified offset in the model". It is
**fresh treatment landing inside the same quarter as the US anniversary, working against it.** Because we
carry it at zero, the mechanism's 3Q26 is the **bottom** of its own band on this term.

**What the mechanism assumes about the US lap partiality.** A **full** lap — i.e. the entire +2.40 NA points
come out in 3Q26. That is the aggressive reading of a genuinely ambiguous date. The 3Q25 letter (official,
ledger D008) says "In August, we launched our Reserve Now, Pay Later payment option within the U.S."; the
3Q25 call says the launch was at the beginning of Q3. The ledger's own note: "Treat the in-quarter ramp date
as a range July to August 2025, not a point." If the mid-August date governs, roughly **6 of 13 weeks** of
3Q25 carried RNPL, so about 6/13 of the lift is *not* yet lapped in 3Q26 and the correct term is
`+ (6/13) × 2.40 × 0.288 = +0.32` points of total nights, not zero. Management also told us the US effect
itself ramped across two quarters (ledger D034: "Over the course of Q4, we began merchandising up funnel…
We saw that that was incremental to lift as well"), which pushes the same way. The unified RNPL module's
own M1 for 3Q26 is **+0.304** — a positive number in the lap quarter — described as the partial US lap net of
the July expansion. Our mechanism carries **0.00**. Both of the 3Q26-specific unquantified terms therefore
point up from the base, and §4 sizes them at +0.32 and +0.30.

### 2.3 4Q26: reconciling the mechanism with DEC-0019, and the 0.78-versus-0.742 problem

**DEC-0019 committed 131.8m, +8.12%, band 131.7–132.7**, built as `8.90 (PR #32 reference) − 0.78 (ex-NA
fee-and-cancellation lap at a 45% split) = 8.12`. The mechanism assembles 4Q26 from the identity instead:

```
NA 4Q26     = 3.31  (the whole NA bundle has lapped: RNPL in 3Q26, fee+cancel in 4Q26)
ex-NA 4Q26  = ( 9.94 − 0.282 × 7.00 ) / 0.718                                        = +11.095%
lap         = 0.45 × 1.649                                                           = −0.742
total       = 0.282 × 3.31 + 0.718 × 11.095 − 0.742 = 0.933 + 7.966 − 0.742          = +8.157%
level       = 121.9m × 1.08157                                                       = 131.84m
```

**+8.157% versus DEC-0019's +8.12% is 0.037pp, and it is pure rounding.** PR #32's reference "8.9" is a
rounding of 132.7/121.9 = **8.859**; `06_pass_line.csv` test 6 re-derives the exit at **8.157** against bridge
v3's 8.12 and passes it with the note "(rounding of 132.7/121.9 in N memo)". **Both routes give 131.8m to the
0.1m the company discloses**, so DEC-0019's committed level is unchanged and no decision needs reopening.

**The 0.78-versus-0.742 inconsistency, resolved.** `final_nights.md` §4 quotes the 4Q26 lap as **0.78** and
§5.1 quotes the same leg in 2027 as **0.742**, which reads like an error. It is not; it is one parameter
computed on two different NA shares:

| file | ex-NA bundle, points of total | NA share used | fee/cancel lap at 45% |
|---|---:|---:|---:|
| `data/processed/overnight2/D/D1_exna_4q26_gap.csv` (WS-D) | 1.752 | 0.266 (PR #32's **2027** share) | **0.79** (the file rounds the 45% midpoint to 0.78) |
| `06_fy27_path_v2/06_assumptions.csv` `exna_bundle_total_pts` | **1.649** | **0.288** (the 3Q26 share) | **0.742** |
| the arguably-correct identification weight | 1.635 | 0.291 (the **1Q26** share, the quarter D032 refers to) | 0.736 |

`06_assumptions.csv` names the discrepancy in its own source string: "3.0 − 0.288 × 4.69 = 1.65; the figure N
memo / WS-D used (D1_exna_4q26_gap: 100% case = 1.75 at PR #32's 0.266 weight)". **Governing value: 1.649 and
0.742**, because that is what the committed 06 build, bridge v3 and every 2027 quarter run on, and because a
4Q26 lap should not be weighted by a 2027 share. The residual question — whether the identification weight
should be 0.291 rather than 0.288 — is worth 0.006 points of nights, i.e. 0.008m, and is not worth a rebuild.
The whole 0.78-vs-0.742 spread is **0.05pp of 4Q26 growth, about 0.06m nights**.

**A second live conflict, unresolved and on the record.** `D1_prereg_thresholds.csv`'s 4Q26-guide row says the
omitted global lap is "worth **0.9 to 1.8 points**". `D1_exna_4q26_gap.csv`, written by the same script in the
same run, marks the 0.7-share (1.22pt) and 1.0-share (1.75pt) rows as
`consistent_with_4q25_disclosure = no`, because they imply a 4Q25 bundle of 2.6–3.1 points against
management's "over 200 basis points". The admissible range is **0.70 to 0.88**. Two files from one folder
disagree by a factor of two; the gap file governs, and the thresholds file needs a dated correction (§9).

**The out-of-sample check that makes the split more than an assertion.** In 4Q25 ex-NA RNPL was **zero** (it
went live 17 Feb 2026), so the ex-NA bundle in 4Q25 was the fee and cancellation legs **alone**. At the 45%
split that gives a 4Q25 global bundle of `0.288 × 4.69 + 0.45 × 1.752 = 1.35 + 0.79 = 2.14` points — clearing
management's "over 200 basis points" (ledger D014) with very little room. At 70% it is 2.58 and at 100% it is
3.10, both of which contradict ">200bp" read as a number near 2. (On the **governing** 1.649 ex-NA bundle the
same check gives `1.35 + 0.742 = 2.09` — still clearing ">200bp", but by 9bp rather than 14bp. A second reason
the 40–50% window is the honest one and 70%-plus is not.) 4Q25 is a quarter PR #32 was **not** fitted
on, which is what makes this a check rather than a calibration. By contrast the 1Q26 agreement (3.1 points
against "approximately three points") is **agreement by construction** and must never be quoted as a test.

### 2.4 2027, and DEC-0025

**DEC-0025** committed the bridge path **169.02 / 157.10 / 155.96 / 139.77, FY27 621.84m, +6.642%**, with the
ledger-dated lap schedule (1Q27 167.1) carried as open item **D-11**. This file reproduces all four quarters
**to three decimals** from the identity and the named parameters — `06_nights_build.csv` base rows 8.206 /
5.934 / 6.229 / 6.045 against the mechanism's 8.206 / 5.934 / 6.229 / 6.045 (receipt
`receipt_n2_mechanism.json`, stdout "Cross-check against committed files").

Two structural choices inside it, both disclosed:

- **The fee/cancellation lap is carried flat at −0.742 through all four 2027 quarters, not re-applied.** It is
  already inside the adopted 4Q26 exit; holding it flat keeps the level effect without charging it twice. This
  is what avoids **D-11**, the ~0.8pp double count that arises if you adopt the 4Q26 ex-NA lap *and* take
  PR #32's 1Q27 row (a flat −1.75 from 1Q27 with nothing in 4Q26) as written.
- **The ex-NA RNPL lap is −0.907 at full phase and −0.363 in 1Q27**, a 0.40 phase fraction because the
  international rollout ran 17 Feb–4 Mar 2026, roughly the last 5–6 of 13 weeks of 1Q26. `06_assumptions.csv`
  marks the fraction `is_judgement = True`. **Assumed.**

The 2Q27 step down of **−2.272pp** from 1Q27 decomposes exactly: RNPL phase deepening **−0.544**, the event
term swinging from +1.0 to −0.5 (**−1.500**), and **−0.227** as the ex-NA rate decays 0.321pt. Those three sum
to −2.271.

**One consequence of DEC-0028 that fixes an existing defect.** `final_nights.md` §5.1 warning 1 says the 2027
y/y figures are computed against a stale FY26 that still carries 3Q26 at 146.813m rather than the adopted
146.3m, so FY27 "would be +6.73% rather than +6.64%" once re-based. **DEC-0028 removes that problem**: the
mechanism's own 3Q26 is 146.813m, which is exactly the number `06_revenue_path_3q26_4q27_v2b.csv` already
carries. FY26 = 156.2 + 148.3 + 146.813 + 131.798 = **583.111m**, FY27 = **621.841m**, **+6.642%** — internally
consistent, no cross-lane re-run needed. Open item 5 of `final_nights.md` §7.4 is closed by this design.

---

## 3. What management disclosed, and when

Every row below is in `data/processed/overnight2/D/rnpl_statement_ledger.csv` (60 dated statements, 57
verified verbatim) unless another file is named. `official` means an SEC-filed shareholder letter or 10-Q, or
an Airbnb newsroom page; `mirror` means a transcript page on stockanalysis.com rather than the IR PDF.

### 3.1 The bundle contribution timeline

| date | period | what was said | ledger row | official / mirror |
|---|---|---|---|---|
| 2025-11-06 | 3Q25 | "The introduction of Reserve Now, Pay Later helped drive the acceleration of Nights and Seats Booked in North America during Q3 2025." No magnitude. | D008 | **official** (3Q25 letter) |
| 2026-02-12 | 4Q25 | "In total, we estimate these three features delivered **over 200 basis points** of growth in nights booked and roughly 300 basis points of growth in GBV in Q4." | **D014** | **mirror** (4Q25 call, stockanalysis.com) |
| 2026-05-07 | 1Q26 | "In total, we estimate these three features delivered **approximately three points** of nights booked growth and approximately four points of GBV growth in Q1." | **D032** | **mirror** (1Q26 call) |
| 2026-08-06 | 2Q26 | **No figure.** "Reserve Now, Pay Later… drove more bookings, longer booking lead times, and contributed to the increase in ADR." | D045 | mirror |

**The provenance asymmetry, stated before a judge finds it: the dates are SEC-filed and the magnitudes are
not.** D012, D013, D024 and D060 — which date the cancellation redesign and both fee tranches to October–
December 2025 and describe them as **global** — are all `official_or_mirror = official`, sourced to
`data/raw/letters/3Q25_d40503dex991.htm` and `4Q25_d58192dex991.htm` with their SEC URLs. The two numbers that
size the bundle, D014 and D032, are **both mirrors**. (The letters themselves are gitignored under
`.gitignore:28`; the quotes live in processed mirrors that name the original filename.)

**RNPL share of GBV** — the metric management moved to when it stopped sizing the bundle:

| date | period | statement | row | provenance |
|---|---|---|---|---|
| 2026-05-07 | 1Q26 | "in Q1, **roughly 20%** of global GBV came from Reserve Now, Pay Later bookings" | D031 | **official** (1Q26 letter) |
| 2026-08-06 | 2Q26 | "Specifically in Q2, **over 20%** of our total GBV was booked using this flexible payment option." | D043 | mirror; the official 2Q26 letter carries no share |
| 2026-02-12 | 4Q25 | ">70% adoption by eligible bookings", footnoted "based on global GBV in Q4 2025" | D022 | official — **a different statistic** from the 3Q25 call's "70% of people offered"; the ledger warns the two must not be chained |

"Over 20%" against "roughly 20%" is **not a measurable increase**, and the share is a GBV share, not a nights
share; converting needs an RNPL-to-non-RNPL ADR ratio that has never been disclosed.

### 3.2 The regional growth statements

The four-region nights paragraph, as the letters print it (mirrored in
`data/processed/overnight/02_kpi_panel_long.csv`, `source_verified = True`, each row naming the letter file):

| period | letter date | North America | EMEA | Latin America | Asia Pacific |
|---|---|---|---|---|---|
| 3Q25 | 2025-11-06 | "mid-single digit growth… representing a sequential acceleration, driven by strong domestic travel" | "mid-single digit growth"; "slightly unfavorable year-over-year comparison… Paris Summer Olympic and Paralympic Games in 2024" | "low-20s growth" | "mid-teens growth" |
| 4Q25 | 2026-02-12 | "mid-single digit growth" (domestic, longer lead times) | "high-single digit growth… an acceleration compared to Q3 2025" | "high-teens growth" | "mid-teens growth" |
| 1Q26 | 2026-05-07 | "high-single digit growth… a modest acceleration compared to Q4 2025" | "mid-single digit growth" | "high-teens growth" | "high-teens growth" |
| 2Q26 | 2026-08-06 | "high-single digit growth" (panel: "highest in almost three years") | "high-single digit growth… accelerating from Q1 2026" | "**approximately 20% growth**" | "high-teens growth" |

Three genuinely quantified ex-NA statements exist and then stop:

- **1Q25 letter:** "Excluding North America, Nights and Experiences Booked grew **11%** year-over-year in
  Q1 2025." (`02_kpi_panel_long.csv:792`, metric `nights_yoy_ex_na_pct`.) WS10's estimate for that quarter is
  10.55% — the one clean back-test of the whole ex-NA construction, and it is 0.45pp low.
- **2Q25 and 3Q25 letters:** nights ex-NA grew "double-digits", with North America "approximately 30% of total
  Nights and Seats Booked."
- **Nothing from 4Q25 onward.** `10_regional_panel_quarterly.csv`'s `ex_na_nights_growth_pct_disclosed` and
  `na_share_of_nights_pct_disclosed` columns are empty from 4Q25.

The 2Q26 10-Q's only regional nights sentence is qualitative and confirms the rank order: growth "led by Latin
America and Asia Pacific… **North America and EMEA grew more moderately**".

### 3.3 The Middle East headwind

**This is the only cancellation shock Airbnb has ever sized in nights-growth points.**

- **1Q26 letter, 7 May 2026 (official):** "In Q1 2026, Nights and Seats Booked grew over 9% year-over-year,
  despite increased cancellations from the Middle East conflict. **Absent the impact of the conflict, we
  estimate growth of Nights and Seats Booked would have been approximately 10% year-over-year**, an
  acceleration compared to Q1 2025." (ledger **D042**, official.)
- **1Q26 letter outlook (official):** "In Q2 2026, we expect Nights and Seats booked growth to slightly
  decelerate, relative to Q1 2026, **assuming an estimated roughly 100bps headwind related to the conflict in
  the Middle East.**"
- **1Q26 call, Mertz:** "Nights and seats booked grew 9% after accounting for an approximate 100 basis point
  headwind from the conflict in the Middle East."
- **2Q26 letter (official):** "Following the headwinds we saw last quarter related to the ongoing conflict in
  the Middle East, we've observed a steady recovery of demand trends within the region." **No size.**
- **2Q26 call, Mertz:** "the impact to our business from the conflict was **less than we had anticipated**"
  and, for the guide, "**In Q3, we are not assuming any significant impact related to the conflict in the
  Middle East.**"

That last sentence is why the mechanism carries **zero** Middle East term in 3Q26 and 4Q26, and why the +1.0pt
term sits in **1Q27** as a lap of the 1Q26 base. It is also the weakest event term in the build: management
sized the 1Q26 *actual* at ~100bp but then said the realised 2Q26 impact was smaller than the 100bp they had
assumed, so lapping a full 100bp in 1Q27 may be generous (§7).

### 3.4 The World Cup language

Management has **never put a points figure on an event**, in eight event discussions since 1Q24
(`docs/pitch-forecasts/questions/risk-world-cup-quantified-small/datasets/r15_v2_event_record.csv`,
`points_figure = "no points"` in all eight). What they said:

- **1Q26 letter:** "we expect to host more guests than at any event in Airbnb's history"; "since beginning our
  outreach in October, **over 100,000 homes** across the 16 World Cup host cities have listed on Airbnb for the
  first time."
- **1Q26 call:** for past World Cups and Olympics "a lot of the booking activity happens close to the actual
  games."
- **2Q26 letter:** "Airbnb hosted **millions of guest arrivals** during the tournament… More than **150,000
  homes** across host cities were listed on Airbnb for the first time."
- **2Q26 call:** "**While bookings from any single event may be temporary**, the brand awareness, the trust,
  and new hosts these partners create benefit our business long after the event ends"; "there was **no single
  product**, there's no single partnership or initiative that explains our results."

The nights consequence follows from the booking/stay distinction, which is WS10's: **Nights and Seats Booked
is a booking-date metric**; the tournament ran 11 June to 19 July 2026, so the bulk of World Cup nights were
**booked in 2Q26** and stayed in 2Q26–July 2026. WS10's own note on the record: the World Cup gives **no lift
to 3Q26 booked nights**. It enters this line exactly once, as the **−0.5pt 2Q27 lap** — the assumed lap of a
pull-forward the company never sized.

### 3.5 The 2Q26 10-Q "higher cancellation rates" sentence

`data/raw/regulatory/quantification/abnb_2026q2_10q.html`, Part I Item 2, MD&A → Key Business Metrics and
Non-GAAP Financial Measures → **Gross Booking Value** subsection. Filed **6 August 2026** (signature block:
Chesky and Mertz, "Date: August 6, 2026"; period end 2026-06-30). One occurrence in the document, verbatim:

> "To date, RNPL bookings, which require no payment at the time of booking, **have experienced higher
> cancellation rates than historic bookings** in which some or all of the cash was received at the time of
> booking."

Surrounding context, same paragraph: "Our flexible payment options allow guests to defer a portion or all of
their payment from the time of booking to a date closer to stay. In 2025, we launched RNPL and expanded it
internationally in 2026… As adoption of RNPL and our other flexible payment options continues to grow, the
timing among GBV, revenue, and cash receipts may become less correlated."

**Provenance: official, audited-language MD&A, not a transcript.** This matters because it is the one part of
the cancellation story that does not depend on a mirror. It is also the risk-factor language in D059, which
names RNPL as a forward-looking risk to **Nights and Seats Booked specifically**.

### 3.6 The 3Q26 guide

2Q26 shareholder letter, 6 Aug 2026, ledger **D052**, official: "We expect year-over-year GBV growth to be in
the mid teens, **driven by low double-digit growth in Nights and Seats Booked** and a moderate increase in ADR
due to mix shift and price appreciation." The guide is a **bucket, not a company range**. The ≥10.0% → 147.0m
mapping is ours (`nights_baseline_reconciliation.csv`, last row: "'low double digits' mapped to >=10; not a
company range"). The letter was issued with July in hand and with the July eligibility expansion already live.

---

## 4. The band

Two layers, both computed, neither asserted. The script is
`data/processed/pitch_model_v2/receipts/N2/n2_mechanism.py`; the output is `n2_band.csv`.

### 4.1 Layer 1 — the parameter envelope

Eight named parameters, each with a range taken from a disclosure or from an existing judgement flag. The
"low" column is the adverse end for nights growth and "high" the favourable end.

| parameter | low | base | high | where the range comes from |
|---|---:|---:|---:|---|
| NA 3Q25 bucket ("mid-single digit") | 6.0 | 5.0 | 4.0 | WS10 bucket map lo/hi; a **higher** 3Q25 makes the fitted RNPL leg bigger and the fee/cancel leg smaller |
| NA 1Q26 bucket ("high-single digit") | 7.0 | 8.0 | 9.0 | WS10 bucket map lo/hi. WS27: NA has been at the **bottom** of its bucket in 5 of the last 6 quarters |
| global bundle, 1Q26 | 3.0 | 3.0 | 2.0 | D032 "approximately three points"; D014 "over 200 basis points" in 4Q25. A **smaller** global figure means a smaller ex-NA bundle and therefore a smaller lap |
| ex-NA fee/cancel split | 0.50 | 0.45 | 0.40 | `D1_exna_4q26_gap.csv`, pinned 40–50% by the 4Q25 out-of-sample check |
| 1Q27 RNPL phase | 0.50 | 0.40 | 0.30 | `exna_rnpl_lap_fraction_1Q27`, flagged judgement; the dated window is 5–6 of 13 weeks |
| US lap partiality, 3Q26 | 0.00 | 0.00 | 6/13 | letter says August 2025 (≈6 of 13 weeks un-lapped); call says beginning of Q3 (full lap) |
| July 2026 expansion | 0.0 | 0.0 | +0.3 pts | ledger D044, unsized; the module carries +0.1 to +0.3 |
| events (ME 1Q27, WC 2Q27) | 0.0 / −0.75 | +1.0 / −0.5 | +1.0 / 0.0 | 1Q26 letter ~100bp; World Cup never sized (`06_assumptions.csv` bear/bull) |

**One at a time** (swing in points of total nights growth):

| parameter | 3Q26 | 4Q26 | 1Q27 | 2Q27 | 3Q27 | 4Q27 |
|---|---|---|---|---|---|---|
| NA 3Q25 bucket | −0.288 / +0.288 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| NA 1Q26 bucket | −0.288 / +0.288 | −0.130 / +0.130 | −0.193 / +0.193 | −0.286 / +0.286 | −0.283 / +0.283 | −0.277 / +0.277 |
| global bundle 3.0 → 2.0 | 0 / 0 | 0 / +0.450 | 0 / +0.670 | 0 / +1.000 | 0 / +1.000 | 0 / +1.000 |
| fee split | 0 / 0 | −0.082 / +0.082 | −0.049 / +0.049 | 0 / 0 | 0 / 0 | 0 / 0 |
| 1Q27 phase | 0 / 0 | 0 / 0 | −0.091 / +0.091 | 0 / 0 | 0 / 0 | 0 / 0 |
| US lap partiality | 0 / **+0.319** | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| July expansion | 0 / **+0.300** | 0 / +0.300 | 0 / +0.300 | 0 / +0.300 | 0 / 0 | 0 / 0 |
| events | 0 / 0 | 0 / 0 | **−1.000** / 0 | −0.250 / +0.500 | 0 / 0 | 0 / 0 |

**The full envelope**, all eight moved together:

| period | low y/y | **base y/y** | high y/y | low (m) | **base (m)** | high (m) |
|---|---:|---:|---:|---:|---:|---:|
| 3Q26 | +9.311 | **+9.89** | +10.949 | 146.04 | **146.8** | 148.23 |
| 4Q26 | +7.931 | **+8.16** | +9.055 | 131.57 | **131.8** | 132.94 |
| 1Q27 | +6.858 | **+8.206** | +9.401 | 166.91 | **169.02** | 170.88 |
| 2Q27 | +5.396 | **+5.934** | +8.022 | 156.30 | **157.10** | 160.20 |
| 3Q27 | +5.941 | **+6.229** | +7.517 | 154.72 | **155.96** | 159.37 |
| 4Q27 | +5.757 | **+6.045** | +7.333 | 139.14 | **139.77** | 142.69 |
| FY27 | +6.007 | **+6.642** | +8.106 | 617.07 | **621.84** | 633.14 |

Three things to read off that table. First, **the 3Q26 band is asymmetric upward** (−0.58 / +1.06), because
the two 3Q26-specific unquantified terms — the July expansion and the US lap partiality — are both carried at
zero in the base. The mechanism is the conservative reading of its own inputs. Second, the FY27 high of
**+8.106%** lands within 0.06pp of D3's independently-derived "lap-treatment flip" sensitivity of **+8.17%**
(`06v_fy27_path_check`, `base_no_exna_lap_2027`), from a completely different route — the envelope and the
flip are the same question asked twice. Third, **the envelope does not reach the Street on any quarter**:
the 3Q26 high of 148.23m is still 0.77m below the Street's 149.0m, and the 4Q26 high of 132.94m is 1.06m below
134.0m.

**What is *not* in this envelope, and it is the biggest thing:** WS10's own ex-NA forecast rates. They are
held at base in every cell above. WS10's bear/bull ex-NA rates for 4Q26 are 8.206 and 13.304 against a base of
11.095, which is ±2.2pp of ex-NA, i.e. ±1.6pp of total nights — larger than everything in the table combined.
That is a demand forecast, not a disclosure, and putting it in the band would turn a mechanism claim into a
demand claim. It is stated here instead.

### 4.2 Layer 2 — the print-error band

The parameter envelope is *not* a forecast-error band. For the printed number the honest object is the
walk-forward RMSE of the things that have actually been scored on this KPI:

| object | window | n | walk-forward RMSE (pp) | ratio vs naive |
|---|---|---:|---:|---:|
| reviews stays index | W2, 1Q24–2Q26 | 10 | **1.475** | 0.683 |
| reviews stays index | W1, 1Q23–2Q26 | 14 | **2.408** | 0.837 |
| best external series (NTTO overseas, INE, TSA, CPI) | 2023Q1–2026Q2 | 9–11 | 1.61 – 2.00 (in-sample residual sd) | 0.743 – 0.976 |
| hotel RevPAR (MAR/HLT) → nights | W2 / W1 | 10 / 14 | — | 0.68 / 0.755 |

So the print-error band on any 3Q26 point is **±1.5 to ±2.4pp**. Applied to the mechanism's +9.887%:

| band | y/y range | level range (m) |
|---|---|---|
| ±1.475pp (reviews index, W2) | +8.41 to +11.36 | **144.8 – 148.8** |
| ±2.408pp (reviews index, W1) | +7.48 to +12.30 | **143.6 – 150.0** |

**The sentence for the memo:** the mechanism band is 146.0–148.2m and the print band is 144.8–148.8m at one
walk-forward standard error; we publish the point as 146.8m and the print as a range. Note that the Street's
149.0m sits outside the tighter band and just inside the wider one — which is the honest way to say we are
below the Street without claiming a precision nobody on this KPI has.

For pre-registration and 6 Nov scoring, **DEC-0004's band of 8.5–11.0% stands** (it is what PREREG INT-02
scores against); the envelope above is the *mechanism's* band and does not replace it.

---

## 5. The constellation of cross-checks for 3Q26

The CSV is `docs/pitch-model-v2/lines/figures/nights_constellation_3q26.csv` (columns `source`,
`read_yoy_pct`, `level_m`, `method`, `window`, `ratio_vs_naive`, `date`, `independent_of_mechanism`).

| source | read y/y | level (m) | method | window | ratio vs naive | date | independent of the mechanism? |
|---|---:|---:|---|---|---:|---|---|
| **mechanism (base)** | **+9.887** | **146.81** | disclosed regional buckets + fitted NA legs; US RNPL lapped in full; July expansion zero | forward build, no window exists | — | 2026-09-18 | **no** |
| reviews stays index, raw | +10.041 | 147.01 | OLS of printed nights y/y on the review-date index, 14 quarters, slope 0.3221, r 0.862 | fit 1Q23–2Q26 | 0.683 (W2) | 2026-09-14 | yes |
| reviews stays index, W2 bias-corrected | +9.523 | 146.32 | raw less the index's own +0.518pp W2 walk-forward mean error | W2, n 10 | 0.683 | 2026-09-14 | yes |
| reviews stays index, W1-corrected | +8.409 | 144.84 | raw less +1.632pp W1 mean error | W1, n 14 | 0.837 | 2026-09-14 | yes |
| external stack median, 12 series | +9.232 | 145.93 | median of 12 in-sample single-series fits | fit 2023Q1–2026Q2 | — | 2026-09-06 | yes |
| — NTTO I-94 overseas arrivals, qtd 1m | +9.173 | 145.85 | single-series OLS | 2023Q1–2026Q2 | **0.743** | 2026-09-06 | yes |
| — INE Spain hotel nights, foreign | +9.138 | 145.81 | single-series OLS | 2023Q1–2026Q2 | 0.839 | 2026-09-06 | yes |
| — TSA throughput, qtd | +7.455 | 143.56 | single-series OLS | 2023Q1–2026Q2 | 0.924 | 2026-09-06 | yes |
| — CPI lodging away from home, SA | +11.909 | 149.51 | single-series OLS | 2023Q1–2026Q2 | 0.956 | 2026-09-06 | yes |
| hotel RevPAR (MAR/HLT) → nights | no 3Q26 point until 4 Nov | — | peer-print read-through; the best external feature on this KPI | W2 / W1 | **0.665–0.68** / 0.755 | 2026-09-06 | yes |
| BEA hotels nominal → nights | no clean 3Q26 point | — | monthly accommodation spend read-through | W2, n 10 | **0.71** | 2026-09-06 | yes |
| unified RNPL cohort module, base | +9.49 | 146.3 | the 9.89 mechanism reference less M1 +0.304, M2 −0.113, M3 −0.019, M4 −0.568 | forward build | — | 2026-09-16 | **no** |
| H1–H2 seasonal bridge, pattern only | +9.492 | 146.3 | 2023–25 seasonal transition applied to 2026 H1; no lap, no event | pattern | — | 2026-09-12 | yes |
| **Street (Bloomberg MODL)** | **+11.527** | **149.0** | mean of 28 estimates; low 147.0, high 151.0 | — | — | 2026-09-12 | yes |
| management guide, 2Q26 letter | ≥ +10.0 | 147.0 | "low double-digit" bucket; the ≥10.0% mapping is **ours** | — | — | 2026-08-06 | yes |

**How to read the constellation, honestly.**

- **Thirteen of the fifteen reads are independent of the mechanism's inputs.** The two that are not are the
  mechanism itself and the RNPL cohort module, which starts from the mechanism's 9.89 reference and subtracts
  four RNPL terms. The H1–H2 bridge is a pure seasonal-pattern object with no lap and no event and does not
  touch WS10.
- **The cluster is real and it is below the Street.** Ten of the eleven non-Street, non-guide reads sit
  between **+7.4% and +10.1%**, and their median is **+9.49%**. The single exception is CPI lodging at +11.9%,
  whose walk-forward ratio is 0.956 — barely better than doing nothing. Only two reads sit above the
  mechanism: that CPI series and the raw reviews index (+10.0%, before its own measured bias correction).
- **What the constellation is not.** It is *not* twelve independent forecasts. Five of the external twelve are
  Spanish INE series; every external fit is labelled "in-sample fit on full window" in its own file; and the
  strongest of them (hotel RevPAR) has **no 3Q26 reading at all** until Marriott prints on 4 November. The
  correlation of hotel RevPAR with nights halves when 2023 is dropped (0.88 → 0.45), which is the signature of
  a common-deceleration trend artefact, and note 08 says so. Two files also give that feature two slightly
  different W2 ratios — **0.68** in `08_altdata-index-and-backtests.md` §3 ("Hotel RevPAR y/y (MAR/HLT)") and
  **0.665** in D1 §6 ("HLT RevPAR, full quarter"); they are different constructions of the same idea and both
  are quoted rather than reconciled.
- **The reviews index carries a caveat we must state first.** It beats naive on both windows (0.683 and 0.837
  are both below 1.0) but clears the team's pre-registered 0.75 survivor hurdle on **neither** — on W1
  outright, and on W2 once the 2023 training quarters are re-read from a fresh vintage (0.757). The governing
  instruction is `SR_QUARTER_SUBMISSION_READINESS_v1.md`: "Do not present the old 0.68x result as a current
  two-window validated forecast." **This is precisely why DEC-0028 moved the index out of the spine.** As a
  corroborating read it is fine; as the thesis it was a 14-point regression that fails its own hurdle.
- **One data defect in the cross-check layer, flagged not fixed:** the reviews index weights regions with a
  constant labelled `FY25_NIGHTS_SHARE` that is actually the 2Q26 quarterly share (§2.1, point 3). It
  overweights EMEA by 1.3pp and underweights NA by 1.3pp relative to the 10-K. That is a cross-check, not the
  line, and re-weighting is outside this design's lane.

---

## 6. Why the Street's bar assumes acceleration

**The sequence of printed nights growth** (`data/processed/abnb_driver_history_quarterly.csv`, `nights_m_yoy_pct`):

| 3Q22 | 4Q22 | 1Q23 | 2Q23 | 3Q23 | 4Q23 | 1Q24 | 2Q24 | 3Q24 | 4Q24 | 1Q25 | 2Q25 | 3Q25 | 4Q25 | 1Q26 | 2Q26 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 25.09 | 20.16 | 18.61 | 10.99 | 13.54 | 12.02 | 9.50 | 8.69 | 8.48 | 12.35 | 7.92 | 7.43 | 8.79 | 9.82 | 9.15 | 10.34 |

**How many of the last 16 prints accelerated — a correction to the record.** Memo v3 says the Street's bar
"implies acceleration for only the **fourth** time in 16 prints". Recomputed from
`data/processed/predictive/02_peer_readthrough_panel.csv` (`abnb_nights_accel_pp`, the y/y change in the y/y
rate), the last sixteen prints contain **six** accelerations — 3Q22 (+0.30), 3Q23 (+2.55), 4Q24 (+3.87),
3Q25 (+1.36), 4Q25 (+1.03), 2Q26 (+1.19) — or **five** if you require the acceleration to exceed half a point.
Memo v3's own base-rate row elsewhere says "n 5". **The defensible sentence is "five of the last sixteen",
not four**, and it should be corrected before submission. The claim survives the correction: five in sixteen
is 31%, and the Street's 3Q26 bar asks for a **+1.18pp** acceleration in the quarter the US product leg laps.

**The guide history, which is why the Street carries the guide forward.** From
`data/processed/overnight/02_guidance_ledger.csv`, metric `nights_yoy_pct` — 17 nights descriptors since 2Q22,
16 resolved:

| guide type | n | outcome |
|---|---:|---|
| directional ("stable", "moderate", "higher than") | 14 | **13 met**; the single miss is 2Q26, where management guided a slight deceleration and nights **accelerated** to +10.34% — an upside miss |
| bucket ("mid-single-digit", "high-single-digit") | 2 | **both printed above the range** (4Q25 guided 4–6, printed 9.82; 1Q26 guided 7–9, printed 9.15) |
| bucket, pending | 1 | 3Q26, "low double-digit", issued 6 Aug 2026 |

**Management has never printed nights below a guided bucket or on the wrong side of a directional guide.** An
analyst who carries the guide forward one-for-one is following a 16-for-16 record. That is what the Street's
149.0m is: the guide's floor mapped to ≥10%, plus the 2Q26 beat carried forward. It is not irrational; it is
an extrapolation of a delivery record.

**What management actually said on 6 August 2026.** The letter (D052): "We expect year-over-year GBV growth to
be in the mid teens, driven by **low double-digit growth in Nights and Seats Booked**". The call (D044): "in
July, we expanded the types of bookings eligible for Reserve Now, Pay Later." And on the Middle East: "In Q3,
we are not assuming any significant impact." So the guide was set with July in hand, with the expansion
already live, and with no event or conflict assumption inside it.

**What +11.5% requires, on our own identity.** 149.0m on the printed 133.6m base is **+11.527%**. Holding the
other side of the identity at the mechanism's values:

| holding this fixed | the other side must be | versus | what that means |
|---|---|---|---|
| ex-NA at WS10's +11.62% | **North America +11.30%** | 2Q26's +8% ("highest in almost three years") and a bucket midpoint that WS27 says is more likely 7% | NA must accelerate 3.3pp **in the quarter its own product leg laps** |
| NA at the mechanism's +5.60% | **ex-NA +13.92%** | 2Q26's estimated +12.81% and the FY25 10-K's ex-NA +10.95% | the rest of the world must accelerate again, to 3 points above its FY25 rate |

For contrast, the **guide floor** of +10.0% requires only NA at +5.99% (against our 5.60%) or ex-NA at +11.78%
(against 11.62%) — both inside noise. **The guide is very reachable; the Street's bar is a different
question.** That distinction is the whole of the nights call: we are not forecasting a guide miss as the base
case, we are saying the consensus number requires an acceleration that the company's own product calendar
argues against.

---

## 7. Falsifiers and tells, pre-registered

### 7.1 The 5 November thresholds

| object | supports us | weakens us | inconclusive | source |
|---|---|---|---|---|
| 3Q26 nights y/y | **≤ +8.5%** (≤ 144.9m) | **≥ +10.3%** (≥ 147.3m) | 8.6% to 10.2% — where our base sits | `PREREG_ABNB-INT-v1.md` INT-02; `D1_prereg_thresholds.csv` |
| a quantified bundle contribution for 3Q26 | none given, or **≤ 1.5 points** | **≥ 2.5 points** | qualitative only (what 2Q26 gave) | `D1_prereg_thresholds.csv` |
| RNPL share of GBV, 3Q26 | flat or down vs 2Q26 while nights decelerate | **≥ 25%** with nights ≥ 10% | 21–24% | same |
| **(unearned fees y/y) − (GBV y/y)** | **≤ −18 points** | wider than −8 points | −12 to −18 (in line with 1H26) | `research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md`, STATUS header |
| 4Q26 guide | implies ≤ 7.5% | implies ≥ 9.5% | 7.6–9.4% — **where both our cases sit** | `D1_prereg_thresholds.csv` |

Two corrections that travel with the unearned-fees row, both already on the record. (i) The raw threshold in
`D1_prereg_thresholds.csv` is an absolute y/y (≤ −3% supports, ≥ +6% weakens); the **corrected, governing** rule
is the *difference* against GBV growth, because management predicted (ledger D038, 1Q26 letter, official)
"lower unearned fees in Q1 and Q2 and **higher unearned fees in Q3**", so a weak Q3 print contradicts
management directly. (ii) The 11 Sep proposal to score funds payable instead was **REFUTED** on verification:
the FY2025 10-K Note 2 says host and guest fees are both recorded in unearned fees, so the single-fee
migration moves that line **up** 3–4%, not down. **Unearned fees is the FX-clean, migration-neutral line.**

Our 3Q26 base of +9.89% sits **inside the inconclusive band**, and so does the 4Q26 guide implication on both
of our cases. We should say that out loud rather than have it found: **5 November will very probably not
settle this line.** What it can settle is the *bundle figure* row and the *RNPL share* row, and those are the
two to watch.

### 7.2 The 11 February threshold, and the problem with it

D2's pre-registered test says a 1Q27 guide **at or above +8.2% (169.0m) falsifies the RNPL module outright**,
because that requires both the partial ex-NA lap and the pull-forward reversal to be absent. **Our adopted
base for 1Q27 is +8.206% / 169.0178m — numerically on the kill line.**

The two objects are not on the same basis, and the arithmetic says exactly where the mismatch is. The module's
8.17 reference carries **no Middle East event term and no partial phase**. The bridge's 1Q27 is:

```
 0.672  NA contribution        (0.291 × 2.31)
+7.638  ex-NA contribution     (0.709 × 10.773)
+1.000  Middle East lap        (event term)
−0.742  fee/cancellation lap   (carried flat from 4Q26)
−0.363  ex-NA RNPL lap         (0.40 phase-in)
=  8.206   as adopted          →  169.02m
−  1.000   remove the event    →  7.206  =  167.46m   ex-event
```

(`06_nights_build.csv`'s `sens_no_exna_lap_case_A_pct` of 9.311 for 1Q27 is the same row with both lap terms
removed but the event term **kept**, which is why it is 8.206 + 1.105 and not 8.206 + 2.105.)

So **ex-event our 1Q27 is +7.206% / 167.46m**, comfortably below the 8.2% kill line — and within 0.4m of D2's
independently built, ledger-dated lap schedule of **167.1m**. The whole conflict is the +1.0pt event term.

**Recommendation — which term moves.** Move the **threshold's basis**, not the base case, and do it in writing
before 11 February:

1. **Primary.** Restate the 11 February falsifier as "a 1Q27 guide implying **≥ +9.2%** as guided, i.e. ≥ +8.2%
   after removing the ~100bp Middle East base effect that management itself sized in the 1Q26 letter". This is
   a basis correction with the arithmetic shown, not a goalpost move, and it must be published before the
   event, not after it.
2. **Equally defensible alternative.** Carry the Middle East term at **0.0** in base, which puts 1Q27 at
   **+7.21% / 167.5m** — within 0.4m of D2's ledger-dated schedule, closing **D-11** by convergence rather
   than by choice. The case for it: management said the realised 2Q26 impact was "less than we had
   anticipated", so the 1Q26 ~100bp actual is an uncertain thing to lap in full.
3. **Do not move the phase fraction.** 0.40 is dated from D025–D029 (17 Feb–4 Mar 2026, 5–6 of 13 weeks); it
   is the one 1Q27 parameter with a filing behind it, and moving it to fix a threshold collision would be
   exactly the sin we accuse the Street of.

---

## 8. The judge's attacks, and our answers

**"Your bundle number is one CFO sentence from a transcript mirror."** Correct, and we say it before you do:
D014 and D032 are `official_or_mirror = mirror`, stockanalysis.com transcript pages, not the IR PDF. What is
**SEC-filed** is everything that carries the weight: the dates (D012, D013, D024, D060 — October–December 2025,
described as global, in the 3Q25 and 4Q25 letters), the 1Q26 letter's "roughly 20% of global GBV came from
Reserve Now, Pay Later bookings", and the 2Q26 10-Q's audited "RNPL bookings… have experienced higher
cancellation rates". The mechanism's shape survives if the bundle is 2 points instead of 3 — that is the
`global_bundle_pts` row of §4.1, worth +0.45pp on 4Q26 and +1.0pp on 2H27, and the path still decelerates.

**"You fitted 2.40 and 2.29 on three quarters of North America."** Two, plus an annual anchor, and we would
put it more harshly than that: two **bucket midpoints** (3Q25 "mid-single digit" and 1Q26 "high-single digit")
plus the FY25 10-K's 158/154. The parameters are not error-bounded by any statistical procedure, and D2 says
so: "A fitting error there passes straight through my reproduction untouched." What they do have is an
out-of-sample check: 4Q25, a quarter the fit does not use, reproduces management's "over 200 basis points" at
2.14 points and rules out the 70% and 100% splits. And §4.1 carries the bucket width as a band parameter —
±1 point of NA growth is ±0.29pp of total nights in 3Q26, about ±0.4m. WS27 says the likelier error is that NA
is at the *bottom* of its bucket, which pushes our number down, not up.

**"You assume the July expansion is worth nothing."** We do, and it is the largest unquantified offset in the
build. Management named it and did not size it or name the booking types (D044, a call mirror). Carrying it at
zero makes our 3Q26 the **bottom** of its own band, not the middle: §4.1 puts it at 0 to +0.3 points, which is
0 to +0.4m nights. The module carries +0.1 to +0.3. If you want to give it its top and give the US lap its
partiality, you get 148.2m — still 0.8m below the Street.

**"The index that corroborates you fails your own hurdle."** It does, and that is why **DEC-0028 moved it out
of the spine**. Honest version: the reviews index beats a naive forecast on both windows (0.683 W2, 0.837 W1)
but clears our pre-registered 0.75 hurdle on neither once the 2023 training quarters are re-read from a fresh
vintage (0.757). It is a cross-check, not the thesis. The thesis is a calendar of product anniversaries the
company published itself, and it does not need the index to be a survivor.

**"Hotels decelerating says nothing about Airbnb."** Broadly true, and note 08 says it in the same words:
hotel RevPAR's correlation with Airbnb nights halves when 2023 is dropped (0.88 → 0.45), which is a
common-deceleration artefact, not a read-through. That is why hotel RevPAR appears in the constellation as one
of fifteen reads with its ratio printed beside it, and not as evidence. It is also why we will not have a
hotel read on 3Q26 until Marriott prints on **4 November**, one day before Airbnb.

**"You cannot separate lap from demand."** For most of the path, agreed — and the pre-registered identification
column concedes it in writing: "a guide cut cannot be attributed to cancellations without management saying
so." What **is** separable is dated: the 4Q26 step of −0.742 comes from two SEC-filed letters dating the
cancellation redesign and fee tranche 1 to October–December 2025 and describing them as global. A level gain
that went live then lifts y/y growth in 4Q25–3Q26 and stops lifting it from 4Q26 **whatever demand does**.
Everything else — WS10's ex-NA rate decaying from 10.77 to 9.81 through 2027, North America held at +2.31 —
is a forecast assumption and we label it as one. This is a comp-arithmetic claim, not a demand claim.

**"What if management restates the bundle at 2.5 points?"** Then we are wrong on the gate and we have
pre-registered it: a 3Q26 bundle figure of **≥ 2.5 points** is on the "weakens" side of
`D1_prereg_thresholds.csv`, and the memo's flip rule is nights **≥ +10.3% with a restated bundle of ≥ 2.5
points → we cover.** Mechanically a bigger bundle also makes the *lap* bigger, so a restatement up would raise
3Q26 and lower 4Q26–2027; it damages the print call and strengthens the shape call. The asymmetry is in our
favour on the part of the thesis that matters for FY27.

**"Why should I believe +2.31% North America underlying?"** Because it is what North America was doing before
the products landed, measured two independent ways. The FY2025 10-K prints NA nights at 158m against 154m,
**+2.6%**. A choice model built on US lodging demand, category adoption and the hotel–Airbnb price gap, with
**no product lever at all**, produces +3.31% for 2026 and +2.31% for 2027
(`na_nights_lap_scenarios.csv`, "base: no product lever"). The reconciliation script exists precisely because
the two sides of the house disagreed — "the model gets US +3.3% for 2026 against WS10's NA +7%" — and its
finding is that the model's pre-product run rate and the pre-RNPL NA run rate are the same number. What is
genuinely assumed is the **1.0pt step down from 2026 to 2027**, which is the choice model's own annual rate
change placed on 1Q27; it is worth about 0.29pp of total nights growth per year.

**"Your North America share is 28.8% but the 10-K says 30%."** Correct, and it cuts against us. WS10's shares
are estimated from XBRL regional revenue over a regional ADR index, not disclosed; the FY2025 10-K gives
29.6%. Re-weighting WS10's own cells on the disclosed shares lowers its 3Q26 total from 10.69% to 10.57% and
its 4Q26 from 10.35% to 10.17%, so the estimate **overstates** the starting point by 0.12–0.18pp. We keep
WS10's shares because the committed model and its −0.41pp calibration were built on them, and we state the
bias.

**"Your regional buckets don't even add up."** They don't, by 0.76pp in 1Q26 and 1.06pp in 2Q26, and we carry
the mean of the last four quarters (−0.41pp) as an explicit calibration constant inside the forward totals.
WS10 calls the ±1.1pp residual "the honest error bar on the whole regional layer" and we adopt that language.
WS27 then asks which region is at the wrong end of its bucket and answers North America, in five of the last
six quarters — which is the direction that makes our number lower, not higher.

---

## 9. What changes in the model, and in `final_nights.md`

### 9.1 The 3Q26 base point: 146.8 instead of 146.3

**DEC-0028** moves the 3Q26 base from the reviews index's bias-corrected read (146.3m, +9.5%, DEC-0004 /
DEC-0024) to the mechanism's own output (**146.8m, +9.89%**). The consequence, at **DEC-0008**'s ADR of
**$176.88** and **DEC-0018**'s Street-implied take rate of **17.98%** (V1 §2a: 4744 ÷ (149.0 × 177.06)):

| object | at 146.3m | at 146.813m | change |
|---|---:|---:|---:|
| 3Q26 GBV (nights × ADR, DEC-0018 identity) | $25,877.5M | **$25,968.3M** | **+$90.7M** |
| 3Q26 revenue (GBV × 17.98%) | $4,652.8M | **$4,669.1M** | **+$16.3M** |
| distance to the Street's GBV ($26,355M at 149.0 × 176.88) | −$477.6M | −$386.8M | — |

For scale: +$16.3M of revenue is **0.35%** of the 3Q26 line and about a fifth of the $80M the guide range is
wide ($4,690–4,770M). PREREG D-02's own consequence line put the same switch at "5 bp of take rate". **The switch is a
narrative decision, not a valuation decision** — and that is the honest reason to make it: the mechanism is
the argument we can defend for eight minutes, and the index is the cross-check we cannot defend as a survivor.

Three second-order consequences:

1. **The FY26 denominator is now internally consistent.** `06_revenue_path_3q26_4q27_v2b.csv` already carries
   3Q26 at 146.813m. Adopting the mechanism removes `final_nights.md` §5.1 warning 1 and its "+6.73% rather
   than +6.64%" correction, and closes open item 5 of §7.4 (the cross-lane re-run request). FY26 583.111m,
   FY27 621.841m, **+6.642%**.
2. **4Q26 is unchanged at 131.8m** (DEC-0019). The mechanism's own exit is 8.157% versus the committed 8.12%;
   both give 131.8m to the 0.1m the company discloses.
3. **The β = 0.5 carry question dissolves.** `adopted_q4_states_v2.json` defines 4Q26 as
   `8.1 + 0.5 × (Q3 − 9.5)`. With the 3Q26 base back at 9.89 rather than 9.5 the carry term is
   `0.5 × (9.89 − 9.5) = +0.195`, which would put 4Q26 at 8.32% / 132.0m rather than 131.8m — but the 8.1 was
   built in a world where Q3 was 9.89 in the first place, so the consistent answer is now **no carry**, and
   `final_nights.md` §7.4 item 3 can be closed rather than left open.

### 9.2 Which parts of `final_nights.md` are superseded

| section | status after DEC-0028 |
|---|---|
| §1 table, 3Q26 row (146.3, +9.5%, "reviews stays index raw read less bias") | **superseded**: 146.8, +9.89%, mechanism. The 1Q23–2Q26 printed rows and the 4Q26/2027 rows stand. |
| §1 warning 1 (stale FY26 denominator, "+6.73% rather than +6.64%") | **withdrawn** — the mechanism's 3Q26 is the 146.813m the build already uses |
| §3 in full ("3Q26: why 146.3m, word by word") | **demoted**: it remains the correct and complete account of the reviews index and is the reference for §5's cross-check row, but it is no longer the construction of the base |
| §3.9 ("Why the team baseline 146.8 was retired") | **reversed**, with its three objections answered in §8 here: no walk-forward score (true, and the index's score fails its own hurdle too), unbounded parameters (banded in §4.1), PREREG D-02's ban on mixing a point and a band (moot — the point and the band now come from the same object) |
| §4 (4Q26) | **stands**, with the 0.78 / 0.742 reconciliation in §2.3 here added |
| §5 (2027) | **stands**, with §5.1 warning 1 withdrawn and §5.3's 1Q27 threshold collision resolved by §7.2 here |
| §6 (catalysts), §7.1–7.3 | **stand** |
| §7.4 open items | items **2** (say out loud that 146.3 is a bias correction) and **5** (re-run the bridge on 146.3) are closed by this design; item **3** (β carry) is closed by §9.1 above; items 1, 4, 6, 7, 8 remain open |
| §8 provenance table | stands; §10 here adds the mechanism's rows |

**What must still be fixed and is not this file's lane:** `D1_prereg_thresholds.csv`'s "0.9 to 1.8 points" lap
range (admissible is 0.70–0.88); `LINES.md`'s attribution of FY27 nights +6.4% to `ALPHA_F_RNPL.md`, which
contains no FY27 nights figure; the `FY25_NIGHTS_SHARE` mislabel in `E4_build_index.py` and
`docs/2026-09-11_q3-nowcast-explainer.md:29`; memo v3's bare "0.68x naive"; memo v3's "fourth time in 16
prints" (should be five); and the habit of quoting +17.9% / +16.5% next to a nights number — those are
**revenue** comps, the nights comps are +9.2% and +10.3%.

### 9.3 The parameter table

The heading below is the literal string `analysis/src/pitch_model_v2/qa.py` parses
(`MACHINE_READABLE_HEADING`); it is not a section number in this document's own sequence. Verified with:
`PYTHONPATH=analysis/src python3 -c "import pathlib; from pitch_model_v2 import qa; m=[]; p=qa._dossier_points(pathlib.Path('docs/pitch-model-v2/lines/nights_v2_design.md'),'N2',m); print(len(p), m)"`

### 2a. Model inputs (machine-readable)

| item | scenario | period | point | unit | note |
|---|---|---|---|---|---|
| na_share_3q26 | base | 3Q26 | 0.288 | share | WS10 nights_share_est_pct; prior-year weight. 10-K FY25 share is 0.296 |
| na_share_4q26 | base | 4Q26 | 0.282 | share | WS10 nights_share_est_pct |
| na_share_1q27 | base | 1Q27 | 0.291 | share | assumed: FY25 10-K 29.6 chained with 1H26 NA +8 vs total +9.7; 06_assumptions is_judgement True |
| na_share_2q27 | base | 2Q27 | 0.291 | share | same |
| na_share_3q27 | base | 3Q27 | 0.288 | share | WS10 |
| na_share_4q27 | base | 4Q27 | 0.282 | share | WS10 |
| na_underlying_yoy_pct | base | 2026 | 3.31 | pct | choice model with no product lever; na_nights_lap_scenarios.csv row base no product lever col 2026 |
| na_underlying_yoy_pct | base | 2027 | 2.31 | pct | same, col 2027. The 1.0pt step is the choice model annual rate change placed on 1Q27 |
| na_underlying_yoy_pct | filing | FY25 | 2.597 | pct | FY2025 10-K Geographic Mix 158 over 154; the 10-K prints 3 pct |
| exna_underlying_yoy_pct | base | 3Q26 | 11.621 | pct | WS10 TOTAL 10.29 less NA 7.0 at share 0.288; includes WS10 calibration minus 0.41 |
| exna_underlying_yoy_pct | base | 4Q26 | 11.095 | pct | WS10 TOTAL 9.94 less NA 7.0 at share 0.282 |
| exna_underlying_yoy_pct | base | 1Q27 | 10.773 | pct | linear phasing from the 4Q26 rate to WS10 FY27 10.292; rule is judgement |
| exna_underlying_yoy_pct | base | 2Q27 | 10.452 | pct | same |
| exna_underlying_yoy_pct | base | 3Q27 | 10.131 | pct | same |
| exna_underlying_yoy_pct | base | 4Q27 | 9.810 | pct | same |
| exna_underlying_yoy_pct | filing | FY25 | 10.947 | pct | FY2025 10-K: 375 over 338 nights ex North America |
| bundle_na_rnpl_pts | base | all | 2.40 | pts of NA nights | fitted in PR #32 on 3Q25 alone: bucket 5.0 less FY25 NA 2.6 |
| bundle_na_feecancel_pts | base | all | 2.29 | pts of NA nights | fitted in PR #32 on 1Q26: bucket 8.0 less underlying 3.31 less 2.40 |
| bundle_na_peak_pts | base | 1H26 | 4.69 | pts of NA nights | sum of the two legs |
| bundle_global_pts | filing | 1Q26 | 3.0 | pts of total nights | ledger D032 approximately three points; mirror |
| bundle_global_pts | filing | 4Q25 | 2.0 | pts of total nights | ledger D014 over 200 basis points; mirror; a floor not a point |
| exna_bundle_total_pts | base | all | 1.649 | pts of total nights | 3.0 less 0.288 times 4.69; governing value, 06_assumptions.csv |
| exna_bundle_total_pts | alt | all | 1.752 | pts of total nights | 3.0 less 0.266 times 4.69; the WS-D D1_exna_4q26_gap convention that produces the 0.78 lap |
| fee_split | base | all | 0.45 | share | midpoint of the 40 to 50 pct pinned by the 4Q25 over-200bp check; assumed |
| fee_split | low | all | 0.50 | share | D1_exna_4q26_gap.csv |
| fee_split | high | all | 0.40 | share | D1_exna_4q26_gap.csv |
| lap_fee_pts | base | 4Q26 | -0.742 | pts of total nights | 0.45 times 1.649; first applied 4Q26, carried flat thereafter |
| lap_fee_pts | base | 1Q27 | -0.742 | pts of total nights | carried flat, not re-applied; this is what avoids the D-11 double count |
| lap_fee_pts | base | 2Q27 | -0.742 | pts of total nights | carried flat |
| lap_fee_pts | base | 3Q27 | -0.742 | pts of total nights | carried flat |
| lap_fee_pts | base | 4Q27 | -0.742 | pts of total nights | carried flat |
| lap_rnpl_pts | base | 1Q27 | -0.363 | pts of total nights | 0.40 times 0.907; partial because ex-NA RNPL went live 17 Feb to 4 Mar 2026 |
| lap_rnpl_pts | base | 2Q27 | -0.907 | pts of total nights | full; 0.55 times 1.649 |
| lap_rnpl_pts | base | 3Q27 | -0.907 | pts of total nights | full |
| lap_rnpl_pts | base | 4Q27 | -0.907 | pts of total nights | full |
| phase_1q27 | base | 1Q27 | 0.40 | share | assumed: 5 to 6 of 13 weeks, ramping; 06_assumptions is_judgement True |
| phase_1q27 | low | 1Q27 | 0.50 | share | band |
| phase_1q27 | high | 1Q27 | 0.30 | share | band |
| us_lap_partiality_frac | base | 3Q26 | 0.00 | share | assumed: full US lap, the call reading beginning of Q3 |
| us_lap_partiality_frac | high | 3Q26 | 0.4615 | share | letter reading, August 2025, about 6 of 13 weeks un-lapped |
| july_expansion_pts | base | 3Q26 | 0.00 | pts of total nights | assumed zero; ledger D044 unsized |
| july_expansion_pts | high | 3Q26 | 0.30 | pts of total nights | module carries 0.1 to 0.3 |
| event_3q26_pts | base | 3Q26 | 0.00 | pts of total nights | 2Q26 call: not assuming any significant Middle East impact in Q3 |
| event_4q26_pts | base | 4Q26 | 0.00 | pts of total nights | no event term |
| event_1q27_pts | base | 1Q27 | 1.00 | pts of total nights | laps the roughly 100bp Middle East headwind, 1Q26 letter, official |
| event_1q27_pts | low | 1Q27 | 0.00 | pts of total nights | recurrence case; see section 7.2 recommendation |
| event_2q27_pts | base | 2Q27 | -0.50 | pts of total nights | assumed lap of an unsized World Cup booking pull-forward |
| event_2q27_pts | low | 2Q27 | -0.75 | pts of total nights | 06_assumptions bear |
| event_2q27_pts | high | 2Q27 | 0.00 | pts of total nights | 06_assumptions bull |
| event_3q27_pts | base | 3Q27 | 0.00 | pts of total nights | July 2026 expansion laps here, carried at zero |
| event_4q27_pts | base | 4Q27 | 0.00 | pts of total nights | none |
| calibration_resid_pts | base | all | -0.41 | pts of total nights | WS10 mean reconciliation residual 3Q25 to 2Q26; already inside the WS10 TOTAL rows |
| nights_yoy_pct | base | 3Q26 | 9.89 | pct | mechanism; DEC-0028 |
| nights_yoy_pct | low | 3Q26 | 9.311 | pct | parameter envelope |
| nights_yoy_pct | high | 3Q26 | 10.949 | pct | parameter envelope |
| nights_m | base | 3Q26 | 146.8 | m | 133.6 times 1.0989 |
| nights_m | low | 3Q26 | 146.04 | m | envelope |
| nights_m | high | 3Q26 | 148.23 | m | envelope |
| nights_yoy_pct | base | 4Q26 | 8.12 | pct | DEC-0019; the mechanism exit is 8.157, same level to 0.1m |
| nights_yoy_pct | low | 4Q26 | 7.931 | pct | envelope |
| nights_yoy_pct | high | 4Q26 | 9.055 | pct | envelope |
| nights_m | base | 4Q26 | 131.80 | m | DEC-0019 |
| nights_m | low | 4Q26 | 131.57 | m | envelope |
| nights_m | high | 4Q26 | 132.94 | m | envelope |
| nights_yoy_pct | base | 1Q27 | 8.206 | pct | 06_nights_build.csv base |
| nights_yoy_pct | low | 1Q27 | 6.858 | pct | envelope |
| nights_yoy_pct | high | 1Q27 | 9.401 | pct | envelope |
| nights_m | base | 1Q27 | 169.02 | m | 156.2 times 1.08206 |
| nights_m | low | 1Q27 | 166.91 | m | envelope |
| nights_m | high | 1Q27 | 170.88 | m | envelope |
| nights_yoy_pct | base | 2Q27 | 5.934 | pct | 06_nights_build.csv base |
| nights_yoy_pct | low | 2Q27 | 5.396 | pct | envelope |
| nights_yoy_pct | high | 2Q27 | 8.022 | pct | envelope |
| nights_m | base | 2Q27 | 157.10 | m | 148.3 times 1.05934 |
| nights_m | low | 2Q27 | 156.30 | m | envelope |
| nights_m | high | 2Q27 | 160.20 | m | envelope |
| nights_yoy_pct | base | 3Q27 | 6.229 | pct | 06_nights_build.csv base |
| nights_yoy_pct | low | 3Q27 | 5.941 | pct | envelope |
| nights_yoy_pct | high | 3Q27 | 7.517 | pct | envelope |
| nights_m | base | 3Q27 | 155.96 | m | 146.813 times 1.06229 |
| nights_m | low | 3Q27 | 154.72 | m | envelope |
| nights_m | high | 3Q27 | 159.37 | m | envelope |
| nights_yoy_pct | base | 4Q27 | 6.045 | pct | 06_nights_build.csv base |
| nights_yoy_pct | low | 4Q27 | 5.757 | pct | envelope |
| nights_yoy_pct | high | 4Q27 | 7.333 | pct | envelope |
| nights_m | base | 4Q27 | 139.77 | m | 131.798 times 1.06045 |
| nights_m | low | 4Q27 | 139.14 | m | envelope |
| nights_m | high | 4Q27 | 142.69 | m | envelope |
| nights_m | base | FY26 | 583.11 | m | 156.2 plus 148.3 plus 146.813 plus 131.798 |
| nights_m | base | FY27 | 621.84 | m | sum of the four 2027 quarters |
| nights_yoy_pct | base | FY27 | 6.642 | pct | 621.841 over 583.111 |
| nights_m | low | FY27 | 617.07 | m | envelope |
| nights_yoy_pct | low | FY27 | 6.007 | pct | envelope, on its own FY26 |
| nights_m | high | FY27 | 633.14 | m | envelope |
| nights_yoy_pct | high | FY27 | 8.106 | pct | envelope; compare D3 lap-treatment flip 8.17 |
| print_error_band_pp | base | 3Q26 | 1.475 | pp | reviews index W2 walk-forward RMSE, n 10 |
| print_error_band_pp | high | 3Q26 | 2.408 | pp | reviews index W1 walk-forward RMSE, n 14 |
| street_nights_m | street | 3Q26 | 149.0 | m | Bloomberg MODL 12 Sep 2026 n 28; DEC-0005 |
| street_nights_m | street | 4Q26 | 134.0 | m | Bloomberg MODL 12 Sep 2026 n 28 |

---

## 10. Provenance

Paths are relative to `/Users/theomachado/Citadel-ABNB`.

| # | number or statement | file path | cell or row | receipt | decision |
|---|---|---|---|---|---|
| 1 | printed nights 1Q22–2Q26 and their y/y | `data/processed/abnb_driver_history_quarterly.csv` | `nights_m`, `nights_m_yoy_pct` by (year, q) | `receipts/H0/receipt.json` | DEC-0003 |
| 2 | FY2025 10-K regional nights 158 / 215 / 90 / 70, total 533, +8% | `data/raw/regulatory/quantification/abnb_2025_10k.json` | index 43, Geographic Mix | transcribed at `data/processed/adr/01_regional_annual.csv`; script `analysis/src/adr/01_annual_anchors.py` | — |
| 3 | FY25 NA +2.597%, ex-NA +10.947% | same, recomputed | 158/154; 375/338 | this file | — |
| 4 | NA underlying 3.31 (2026) / 2.31 (2027) | `data/processed/na_nights_lap_scenarios.csv` | row "base: no product lever", cols 2026 / 2027 | `receipts/N2/receipt_na_nights_reconciliation.json` (exit 0, changed []) | DEC-0025 |
| 5 | fitted RNPL +2.40 and fee+cancel +2.29 | `analysis/src/nights_quarterly.py` `fit_product()`; `data/processed/nights_quarterly_na.csv` | `underlying_pts`, `product_pts` | `receipts/N2/receipt_nights_quarterly.json`, `stdout_nights_quarterly.txt` | DEC-0028 |
| 6 | 3Q26 mechanism +9.89% / 146.8m | `data/processed/nights_quarterly_total.csv` | row (3Q26, base, exna_lap False) | same receipt | DEC-0028 |
| 7 | 4Q26 mechanism +8.90% (PR #32) / +8.157% (06 exit) / 8.12% adopted | `nights_quarterly_total.csv`; `06_pass_line.csv` test 6; `h2_bridge_v3_rebased_lines.csv` | `adopted` 8.12, `adopted_mm` 131.8 | `receipts/N2/receipt_n2_mechanism.json`; `receipts/D2/receipt.json` | DEC-0019 |
| 8 | ex-NA bundle 1.649 at s 0.288 vs 1.752 at s 0.266 | `06_fy27_path_v2/06_assumptions.csv` `exna_bundle_total_pts`; `overnight2/D/D1_exna_4q26_gap.csv` | source string names both | `receipts/N2/receipt_n2_mechanism.json` | DEC-0019, DEC-0025 |
| 9 | fee split 0.45, range 0.40–0.50; 70% and 100% ruled out | `data/processed/overnight2/D/D1_exna_4q26_gap.csv` | `pts_missing_from_4q26`, `consistent_with_4q25_disclosure` | `receipt_D1_cohort.json` | DEC-0019 |
| 10 | 4Q25 out-of-sample bundle 2.05 / 2.14 / 2.23 at 40 / 45 / 50% | `data/processed/overnight2/D/D1_bundle_crosscheck.csv` | `pr32_total_pts`, `status = out of sample` | `receipt_D1_cohort.json` | DEC-0019 |
| 11 | "over 200 basis points… roughly 300 basis points… in Q4" | `data/processed/overnight2/D/rnpl_statement_ledger.csv` | **D014**, 2026-02-12, `official_or_mirror = mirror` | `analysis/src/overnight2/D0_rnpl_statement_ledger.py` | DEC-0019 |
| 12 | "approximately three points… approximately four points… in Q1" | same ledger | **D032**, 2026-05-07, mirror | same | DEC-0028 |
| 13 | cancellation redesign announced October 2025, global | same ledger | **D012** (3Q25 letter), **D060** (4Q25 letter), both `official` | same | DEC-0019 |
| 14 | fee tranche 1: PMS hosts from October 2025, most remaining from December | same ledger | **D013**, **D024**, `official` | same | DEC-0019 |
| 15 | July 2026 eligibility expansion, unsized | same ledger | **D044**, 2026-08-06, mirror | same | — |
| 16 | US RNPL launch "In August" (letter) vs "beginning of Q3" (call) | same ledger | **D001**, **D008**; note "range July to August 2025, not a point" | same | — |
| 17 | international rollout 17 Feb–4 Mar 2026, BRL/INR/TRY excluded | same ledger | **D023**, **D025**–**D029**, **D034** | same | DEC-0025 |
| 18 | RNPL share of GBV: roughly 20% (1Q26, official) / over 20% (2Q26, mirror) | same ledger | **D031**, **D043** | same | — |
| 19 | 2Q26: no bundle figure given | same ledger | **D045** | same | — |
| 20 | 3Q26 guide "low double-digit growth in Nights and Seats Booked" | same ledger | **D052**, 2026-08-06, `official` (2Q26 letter) | same | — |
| 21 | Middle East ~100bp, 1Q26 actual and 2Q26 assumption | same ledger | **D042**, `official` (1Q26 letter) | same | DEC-0025 |
| 22 | "In Q3, we are not assuming any significant impact… Middle East" | 2Q26 call, 6 Aug 2026 | mirrored in `docs/pitch-forecasts/questions/bonus-geopolitical-headwind-cited/sources/letters_calls_geopolitical_passages_4Q20-2Q26.txt` | — | — |
| 23 | 2Q26 10-Q "have experienced higher cancellation rates than historic bookings" | `data/raw/regulatory/quantification/abnb_2026q2_10q.html` | MD&A, Key Business Metrics, Gross Booking Value subsection; filed 2026-08-06 | verbatim, single occurrence | — |
| 24 | World Cup never sized, 8 event discussions | `docs/pitch-forecasts/questions/risk-world-cup-quantified-small/datasets/r15_v2_event_record.csv` | `points_figure = "no points"` in all 8 rows | — | DEC-0025 |
| 25 | World Cup gives no lift to 3Q26 booked nights | `data/processed/nights_baseline_reconciliation.csv` | row 1 note; WS10 note §5 | — | — |
| 26 | WS10 regional forecast 3Q26 / 4Q26 / FY27 by region and scenario | `data/processed/overnight/10_regional_forecast.csv` | `nights_yoy_pct`, `nights_share_est_pct`, TOTAL rows carry the −0.41pp calibration | `receipts/N2/receipt_n2_mechanism.json` | — |
| 27 | regional bucket midpoints, shares and residuals 3Q25–2Q26 | `data/processed/overnight/10_regional_panel_quarterly.csv` | `na_nights_yoy_mid/lo/hi`, `ex_na_nights_yoy_est_pct`, `na_nights_share_est_pct`, `residual_vs_total_pp` | same | — |
| 28 | WS10's own caveats (bucket midpoints load-bearing; ±1.1pp; shares estimated) | `research/notes/overnight/10_regional-and-segment-decomposition.md` | "## Caveats" | — | — |
| 29 | NA at the bottom of its bucket in 5 of the last 6 quarters; FY27 bucket band 8.1 / 9.1 / 10.1 | `research/notes/overnight/27_regional-bucket-check.md` | result table | — | — |
| 30 | WS10 share error overstates its own total by 0.12–0.18pp | `research/notes/overnight2/C_consumer-relative-strength-regional-split.md` | line 15 | — | — |
| 31 | 1Q25 letter "Excluding North America… grew 11%" | `data/processed/overnight/02_kpi_panel_long.csv` | line 792, metric `nights_yoy_ex_na_pct`, `source_verified True` | — | — |
| 32 | four-region bucket phrases 3Q25–2Q26 | same file | lines 883–886, 935–938, 986–989, 1035–1038 | — | — |
| 33 | 2027 build: NA 2.31, ex-NA 10.773 / 10.452 / 10.131 / 9.810, laps −0.742 and −0.363 / −0.907, events +1.0 / −0.5 | `data/processed/margin_build/06_fy27_path_v2/06_nights_build.csv` | four base rows | `receipts/D3/receipt.json`; re-derived in `receipts/N2/` | DEC-0025 |
| 34 | 55 assumptions, 10 judgement; `exna_rnpl_lap_fraction_1Q27` 0.40; `exna_phasing_rule` | `data/processed/margin_build/06_fy27_path_v2/06_assumptions.csv` | named rows, `is_judgement` | `receipts/D3/` | DEC-0025 |
| 35 | 2027 levels 169.0178 / 157.1001 / 155.958 / 139.7655; 3Q26 146.813; 4Q26 131.7983 | `06_revenue_path_3q26_4q27_v2b.csv` | rows `<q>,base,nights_mm` | `receipts/D3/receipt.json` | DEC-0025 |
| 36 | FY27 621.8414m / +6.642% on FY26 583.1113m | `06_annual_fy26_fy28_v2b.csv` | rows (FY27, base), (FY26, base) | same | DEC-0025 |
| 37 | mechanism reproduces 06_nights_build to 3dp on all four 2027 quarters | `receipts/N2/n2_mechanism_quarterly.csv`; `stdout_n2_mechanism.txt` | "Cross-check against committed files" | `receipt_n2_mechanism.json` (exit 0) | — |
| 38 | parameter envelope and one-at-a-time sensitivities | `receipts/N2/n2_band.csv` | `parameter`, `swing_lo_pp`, `swing_hi_pp`, `ENVELOPE_*` rows | same receipt | — |
| 39 | reviews index raw +10.041046, slope 0.322138, r 0.861819, band 8.564–11.518 | `data/processed/q3nowcast/E/q3_2026_nowcast.csv` | row (yoy_all, w_reviews, GLOBAL) | `receipts/D1/receipt.json` | DEC-0004 |
| 40 | W2 ratio 0.683209 / bias +0.518452 (n 10); W1 0.837125 / +1.631798 (n 14) | `data/processed/q3nowcast/E/backtest_wf_paths.csv`, `backtest_abnb_quarterly.csv` | feature `GLOBAL\|yoy_all\|w_reviews` | `receipt_E5.json`; `receipts/D1/d1_recompute.py` | DEC-0004 |
| 41 | re-vintaged ratios 0.683 / 0.841 / 0.757 / 0.713 | `data/processed/q3nowcast_v2/E/t1_fail_e5_rerun.csv` | four variants | `receipt_V6.json` | DEC-0004 |
| 42 | "Do not present the old 0.68x result as a current two-window validated forecast" | `docs/revenue-forecast-strategy/05_backtests/SR_QUARTER_SUBMISSION_READINESS_v1.md` | governing instruction | — | DEC-0004 |
| 43 | external stack: 12 nights rows, median +9.2324%, range 6.753–11.961, per-series ratios | `data/processed/q3nowcast/G/G_nowcast_3q26_observable.csv` | rows `target = nights_m_yoy_pct` | `receipt_G2.json` | DEC-0004 |
| 44 | hotel RevPAR 0.68 (W2) / 0.755 (W1); BEA hotels 0.71; correlation halves 0.88→0.45 | `research/notes/overnight/08_altdata-index-and-backtests.md` §3 survivor table; D1 §6 | — | `receipt_G2.json` | — |
| 45 | 598 tests, 29 beat naive, 7 by ≥20%; Google Trends 432 tests, zero survivors on the full window | same note §1, §3 | `08_test_scoreboard.csv` | — | AGENT_BRIEF §2 |
| 46 | unified RNPL module 3Q26 +9.49 (M1 +0.304, M2 −0.113, M3 −0.019, M4 −0.568); 4Q26 +7.61 | `data/processed/rnpl_short_audit/rnpl_nights_module.csv` | rows (base, 3Q26), (base, 4Q26) | `receipts/D2/` | DEC-0004, DEC-0019 |
| 47 | H1–H2 bridge pattern-only +9.4917 | `data/processed/h2_bridge_v3/h2_bridge_v3_rebased_lines.csv`; `nights_baseline_reconciliation.csv` | col `pattern_only` | `receipts/D3/receipt.json` | DEC-0004 |
| 48 | Street 3Q26 149.0m (low 147.0, high 151.0, n 28) and 4Q26 134.0m | `docs/pitch-model-v2/dossiers/V1_v1_street.md` §2a | `street_nights_m` rows; Bloomberg MODL 12 Sep 2026 | licensed aggregate, not in repo | DEC-0005 |
| 49 | Street take rate 17.98% (3Q26) | same §2a | `street_take_rate_pct` | — | DEC-0018 |
| 50 | ADR 176.88 (3Q26) | `docs/pitch-model-v2/dossiers/D4_d4_adr.md`; DECISIONS | ADR card v3 without K | — | DEC-0008 |
| 51 | nights acceleration count: 6 of the last 16 prints (5 above +0.5pp) | `data/processed/predictive/02_peer_readthrough_panel.csv` | `abnb_nights_accel_pp` | computed in this file | correction stated here |
| 52 | 17 nights guide descriptors; 13 of 14 directional met, 2 buckets printed above range, 1 pending | `data/processed/overnight/02_guidance_ledger.csv` | `metric = nights_yoy_pct`, cols `guide_type`, `outcome` | — | — |
| 53 | INT-02 thresholds ≤8.5 supports / ≥10.3 weakens; band 8.5–11.0 | `05_backtests/PREREG_ABNB-INT-v1.md` INT-02 | — | — | DEC-0004 |
| 54 | 5 Nov RNPL tells (bundle ≤1.5 / ≥2.5; share flat-or-down / ≥25%; 4Q26 guide ≤7.5 / ≥9.5) | `data/processed/overnight2/D/D1_prereg_thresholds.csv` | rows as named | `receipt_D1_cohort.json` | — |
| 55 | corrected unearned-fees rule (UF y/y − GBV y/y ≤ −18 supports); funds-payable proposal REFUTED | `research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md` | STATUS header | `analysis/src/rnpl_short_audit/verify_balance_sheet.py` | — |
| 56 | 1Q27 falsifier ≥ +8.2% / 169.0m; adopted base 169.0178m sits on it | `D1_prereg_thresholds.csv`; D2 §2a and §6; `06_revenue_path_3q26_4q27_v2b.csv` | — | `receipts/D2/`, `receipts/D3/` | open; §7.2 recommends the fix |
| 57 | 1Q27 ex-event +7.206% / 167.46m vs D2's ledger-dated 167.1m | computed in this file from `06_nights_build.csv` base row | `total_nights_yoy_pct` less `event_pts` | `receipts/N2/` | — |
| 58 | `D1_prereg_thresholds.csv` says the lap is "0.9 to 1.8 points" (admissible 0.70–0.88) | same file, 4Q26-guide row | contradicts `D1_exna_4q26_gap.csv` from the same run | `receipt_D1_cohort.json` | open |
| 59 | `FY25_NIGHTS_SHARE` 28.3 / 41.6 / 17.9 / 12.3 is the 2Q26 quarterly share, not FY25 | `analysis/src/q3nowcast/E4_build_index.py:45`; `data/processed/adr/04_regional_quarterly_wide.csv` last row | 10-K FY25 shares are 29.6 / 40.3 / 16.9 / 13.1 | — | open, correction stated here |
| 60 | 3Q26 GBV / revenue consequence of 146.3 → 146.813 (+$90.7M / +$16.3M) | computed in this file at DEC-0008 ADR and DEC-0018 take rate | — | — | DEC-0008, DEC-0018, DEC-0028 |
| 61 | what +11.5% requires: NA +11.30% or ex-NA +13.92% | computed in this file on the §2.0 identity | — | `receipts/N2/` | — |
| 62 | kill-list check | `AGENT_BRIEF.md` §6; `research/notes/overnight/14_master-synthesis.md` §11 | no item quoted as ours; near-misses cleared in §5 and §8 | — | — |

**Kill-list check.** Nothing on `AGENT_BRIEF` §6 is quoted here as ours. Four near-misses were checked: (i)
the "+4.05% fee uplift" is not used — fee tranche 2 is carried at **0.0 points of nights**; (ii) "the 120-market
panel as a nights measurement" is the Inside Airbnb listings/calendar panel, a different object from the
123-market review-date stays index, which appears here only as a cross-check with its ratios printed; (iii)
"nothing beats guide × cushion" is not said — the wording used is "no single object beats it on both windows";
(iv) "any FY27 level edge without the +9.2–11.5% band" binds the revenue line, and the FY27 nights figure here
is quoted with its own envelope (+6.01 to +8.11%). The reviews index is quoted with the full three-ratio
sentence (0.68 W2 / 0.84 W1 / 0.76 re-vintaged; clears 0.75 on neither), per DEC-0004.
