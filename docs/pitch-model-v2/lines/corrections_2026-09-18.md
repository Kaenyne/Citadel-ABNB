# Corrections — nights line, pitch model v2, 18 September 2026

**What this file is.** A dated correction note in the repo's convention (`AGENT_BRIEF.md` §8, last bullet:
"If you find an error in an earlier note, do not edit it — write a dated correction in your own note and add
one line to `WORKBOARD.md` under 'Corrections'"). Nothing in an earlier artefact has been edited by this
note. Each entry says what the earlier artefact says, where it says it, what is correct, the evidence, the
decision that authorises the correction, and the consequence.

Written by the nights-line writer while updating `docs/pitch-model-v2/lines/final_nights.md` to version 2.
Governing construction: `docs/pitch-model-v2/lines/nights_v2_design.md`. Decisions: **DEC-0028** to
**DEC-0032**. Web fetches: zero. Paths are relative to `/Users/theomachado/Citadel-ABNB`.

| # | subject | decision | status |
|---|---|---|---|
| 1 | 1Q27 falsifier restated on an event-adjusted basis | DEC-0032 | corrected here, before the event |
| 2 | acceleration count: "fourth time in 16 prints" → five (six on any positive acceleration) | DEC-0032 | corrected here |
| 3 | `FY25_NIGHTS_SHARE` is the 2Q26 quarterly share, not FY25 | DEC-0032 | flagged, not fixed (cross-check layer) |
| 4 | `D1_prereg_thresholds.csv` lap range "0.9 to 1.8 points" vs admissible 0.70–0.88 | DEC-0032 | corrected here; the CSV is another lane's artefact |
| 5 | provenance flag on ledger rows D014 and D032 | DEC-0031 | **resolved 18 Sep by the X3 digger: neither sentence is in any SEC filing** |

---

## 1. The 1Q27 falsifier, restated on an event-adjusted basis (DEC-0032)

**What the earlier artefacts say.** A 1Q27 nights guide **at or above +8.2% (169.0m) falsifies the RNPL
module outright**, because that reading requires both the partial ex-NA lap and the pull-forward reversal to
be absent. The threshold was written on 11 September 2026 and is carried, word for word or in substance, in:

| artefact | row / line |
|---|---|
| `docs/pitch-model-v2/dossiers/D2_d2_nights_4q26_lap.md` | §2a model-inputs rows, lines **40** (`nights_m, breaker, 1Q27, 169.0`) and **43** (`nights_yoy_pct, breaker, 1Q27, 8.17`, "≥ +8.2% falsifies the module outright"); §6 forward-tell table, line **113**; §9 Q5, line **143** |
| `docs/rnpl-short-audit/00_SYNTHESIS.md` | line **38** ("February falsifier — 1Q27 guide ≥ +8.2% (169.0mm) falsifies the module outright"); line **67** |
| `docs/rnpl-short-audit/01_rnpl-nights-mechanics-audit.md` | line **183** |
| `docs/pitch-forecasts/questions/q1-27-nights-guide-above-82/README.md` | line **3** (the question itself: "imply ≥ +8.2% y/y on 156.2m (≥169.0m)? Binary. The RNPL module's pre-registered falsifier") |
| `docs/pitch-forecasts/questions/q1-27-nights-guide-above-82/research-log.md` | line **40** (row 7 of the evidence table) |
| `docs/pitch-forecasts/questions/q1-27-nights-guide-above-82/forecasts/2026-09-17-forecast.json` | `prereg_note` (line **15**); resolver assumption (line **26**) |
| `docs/pitch-model-v2/lines/final_nights.md` **v1** | §5.3 (line **689**), §7.1 "1Q27 guide, 11 Feb" (line **991**), §7.4 item 4 (line **1063**), §8 provenance rows **81** and **85** |
| `docs/pitch-model-v2/lines/nights_v2_design.md` | §7.2 (states the collision and recommends this restatement); §10 row **56** |

**A pointer defect found while grepping, stated rather than edited.** `nights_v2_design.md` §10 row 56 and
`final_nights.md` v1 §8 row 81 both attribute the 1Q27 falsifier to
`data/processed/overnight2/D/D1_prereg_thresholds.csv`. **That file carries no 1Q27 row.** Its seven metrics
are: 3Q26 nights y/y; 3Q26 GBV-minus-nights gap; 3Q26 unearned fees y/y; the backlog conversion ratio; the
4Q26 nights guide; an RNPL GBV share for 3Q26; and whether management repeats a quantified bundle figure.
The 1Q27 falsifier lives in the RNPL-audit files and in D2's own §2a / §6, not in the pre-registration CSV.
Anyone scoring on 11 February should read D2 §6 and `00_SYNTHESIS.md` §2, not the CSV.

**What is correct.** The threshold and our base case are **not on the same basis**, and the whole of the gap
is one term. The module's 8.17 reference carries **no Middle East event term and no partial phase**; the
adopted bridge base carries a **+1.0 point** lap of the ~100bp Middle East headwind management sized in the
1Q26 letter, plus a 40%-phased ex-NA RNPL lap. Restated on the module's own basis, the falsifier is:

> **A 1Q27 guide implying ≥ +9.2% as guided — i.e. ≥ +8.2% net of the ~100bp Middle East base effect the CFO
> disclosed on the 1Q26 call — falsifies the RNPL module.**

**The arithmetic, in full.**

```
adopted 1Q27 base, headline        +8.206%   ->  156.2m x 1.08206  =  169.0178m   (169.02m)
   NA contribution                  0.672    (0.291 x 2.31)
   ex-NA contribution              +7.638    (0.709 x 10.773)
   Middle East lap, event term     +1.000
   fee/cancellation lap            -0.742    (carried flat from 4Q26)
   ex-NA RNPL lap                  -0.363    (0.40 phase-in)

remove the event term              -1.000pp
ex-event 1Q27                      +7.206%   ->  156.2m x 1.07206  =  167.4558m   (167.46m)
D2's ledger-dated lap schedule                                         167.1m      (0.36m apart)

old threshold as written           >= +8.2%  ->  156.2m x 1.082     =  169.0m
restated threshold, as guided      >= +9.2%  ->  156.2m x 1.092     =  170.57m
restated threshold, ex-event       >= +8.2%  ->  167.46m basis

distance from our base to its own kill line
   headline basis   9.200 - 8.206 = 0.994pp
   ex-event basis   8.200 - 7.206 = 0.994pp      ->  1.0 point inside, on either basis
```

So the base that looked like it was sitting **on** its own kill line is, once the two objects are put on one
basis, **a full point inside it**, and the ex-event level (167.46m) is within **0.36m** of D2's
independently built, ledger-dated schedule (167.1m). The `sens_no_exna_lap_case_A_pct` column of
`06_nights_build.csv` reads 9.311 for 1Q27, which is 8.206 + 1.105 and not 8.206 + 2.105, precisely because
that sensitivity removes both lap terms and **keeps** the event term — the same basis mismatch, visible in
the committed file.

**Evidence.** `data/processed/margin_build/06_fy27_path_v2/06_nights_build.csv`, 1Q27 base row
(`na_share` 0.291, `na_yoy` 2.31, `exna_pre_lap_yoy` 10.773, `lap_fee` −0.742, `lap_rnpl` −0.363,
`event_pts` +1.0, `total` 8.206); `06_revenue_path_3q26_4q27_v2b.csv` row `1Q27,base,nights_mm` = 169.0178;
receipts `data/processed/pitch_model_v2/receipts/D3/receipt.json` and
`data/processed/pitch_model_v2/receipts/N2/receipt_n2_mechanism.json` (exit 0, mechanism reproduces
`06_nights_build.csv` to three decimals on all four 2027 quarters). The ~100bp event size is **official**:
1Q26 shareholder letter, 7 May 2026, ledger row **D042** in
`data/processed/overnight2/D/rnpl_statement_ledger.csv` — "Absent the impact of the conflict, we estimate
growth of Nights and Seats Booked would have been approximately 10% year-over-year" — and the same letter's
outlook paragraph, "an estimated roughly 100bps headwind related to the conflict in the Middle East". The
restatement itself is written out in `nights_v2_design.md` §7.2, recommendation 1.

**Decision.** **DEC-0032** ("the 11 Feb 1Q27 falsifier is restated now, by dated correction, on an
event-adjusted basis: ≥ +9.2% headline as guided, i.e. ≥ +8.2% net of the ~100bp Middle East lap").

**Why restating now is a correction and restating in February would be a goalpost move.** Three reasons,
and they are all about timing and disclosure rather than about the number:

1. **The defect is in the basis, not in the outcome.** The threshold was written against an object that
   carries no event term; the base it is now compared with carries one. Comparing them is a units error. The
   correction adds no freedom: the ex-event base (+7.206%) was already in the committed build, and the
   restated line still kills the module on exactly the same economics.
2. **It is published before the information arrives.** The 4Q26 shareholder letter with the 1Q27 descriptor
   is expected ~11 February 2027, nearly five months from today. Nothing about the guide is knowable now, so
   the restatement cannot be selected to survive it. After the letter prints, the same change would be a
   basis chosen with the answer in hand — which is the exact habit we accuse the Street of, and the sin
   `nights_v2_design.md` §7.2 recommendation 3 refuses for the phase fraction.
3. **The old number stays in the record.** This note does not delete "≥ +8.2% (169.0m)" from D2 or from the
   rnpl-short-audit files; it states what basis it was written on and what the same test is on the basis the
   model now runs. Both numbers stay scoreable on 11 February.

**Consequence.** (i) `final_nights.md` v2 §7.1 now carries the restated falsifier, and §7.4's D-11 item is
re-worded so the base is no longer described as sitting *on* the kill line. (ii) The equally defensible
alternative in `nights_v2_design.md` §7.2 — carrying the Middle East term at 0.0 in base, which puts 1Q27 at
+7.21% / 167.5m and closes D-11 by convergence — is **not** taken; the base is unchanged at 169.02m
(DEC-0025), because moving an input to fix a threshold is the thing DEC-0016 forbids. (iii) The forecast
question `q1-27-nights-guide-above-82` resolves on the **as-guided headline** number; its resolver
(`forecasts/2026-09-17-forecast.json`, line 26) should be read against ≥ +9.2%, not ≥ +8.2%, at its next
revision. That is a request to another lane, not an edit.

---

## 2. The acceleration count: "fourth time in 16 prints" should be five

**What the earlier artefact says.** Memo v3: "The Street's bar implies acceleration for only the **fourth**
time in 16 prints." — `deck/drafts/memo_v3_short_2026-09-17.md`, **line 33**. The same sentence is in
`deck/drafts/memo_v2_short_2026-09-16.md` line 33 and `deck/drafts/memo_v1_short_2026-09-16.md` line 11.

**What is correct.** **Five** of the last sixteen prints accelerated, if "acceleration" requires the y/y rate
to rise by more than half a point; **six** on any positive acceleration. Not four.

**Evidence.** `data/processed/predictive/02_peer_readthrough_panel.csv`, column `abnb_nights_accel_pp` (the
year-over-year change in the year-over-year rate), the sixteen prints 3Q22 through 2Q26 — the same window and
the same file `nights_v2_design.md` §6 sources its printed-nights sequence from:

| quarter | nights y/y | acceleration (pp) |
|---|---:|---:|
| 3Q22 | 25.09 | **+0.30** |
| 4Q22 | 20.16 | −4.93 |
| 1Q23 | 18.61 | −1.55 |
| 2Q23 | 10.99 | −7.62 |
| 3Q23 | 13.54 | **+2.55** |
| 4Q23 | 12.02 | −1.52 |
| 1Q24 | 9.50 | −2.52 |
| 2Q24 | 8.69 | −0.81 |
| 3Q24 | 8.48 | −0.21 |
| 4Q24 | 12.35 | **+3.87** |
| 1Q25 | 7.92 | −4.43 |
| 2Q25 | 7.43 | −0.48 |
| 3Q25 | 8.79 | **+1.36** |
| 4Q25 | 9.82 | **+1.03** |
| 1Q26 | 9.15 | −0.67 |
| 2Q26 | 10.34 | **+1.19** |

Six positive: **3Q22, 3Q23, 4Q24, 3Q25, 4Q25, 2Q26**. Five above +0.5pp: the same list without 3Q22's
+0.30. Memo v3's own base-rate row elsewhere already says "n 5", so the memo disagrees with itself.
`nights_v2_design.md` §6 states the recomputation and §10 row 51 carries it.

**Decision.** **DEC-0032** ("also filed as corrections: memo v3 'fourth' → fifth acceleration of 16").

**Consequence.** The defensible sentence is "**five of the last sixteen**" — 31%, not 25%. The claim
survives the correction and barely moves: the Street's 3Q26 bar of 149.0m asks for a **+1.18pp**
acceleration in the quarter the US product leg laps, which is larger than four of the five historical
accelerations. Memo v3 must be changed before submission; this note does not edit the deck.

---

## 3. `FY25_NIGHTS_SHARE` is the 2Q26 quarterly share, not the FY25 share

**What the earlier artefacts say.**

- `analysis/src/q3nowcast/E4_build_index.py`, **line 45**:
  `FY25_NIGHTS_SHARE = {"NAM": 28.3, "EMEA": 41.6, "LatAm": 17.9, "APAC": 12.3}`, described in the file as
  Airbnb's FY25 regional nights shares. It is used at lines 228–229 and 274 to weight regional review growth
  into the global index.
- `docs/2026-09-11_q3-nowcast-explainer.md`, **line 29** ("Problem three: aggregation and composition"),
  repeats the label in prose: "Airbnb's FY2025 regional nights shares (North America 28.3 percent, EMEA 41.6,
  Latin America 17.9, Asia Pacific 12.3)".

**What is correct.** Those four numbers are the **2Q26 single-quarter** shares. The FY2025 shares from the
10-K are **29.6 / 40.3 / 16.9 / 13.1**.

**Evidence.** `data/processed/adr/04_regional_quarterly_wide.csv`, last row (`quarter = 2Q26`):
`nights_share_na_pct` 28.2553, `nights_share_emea_pct` 41.5500, `nights_share_latam_pct` 17.8621,
`nights_share_apac_pct` 12.3325 — the constant to the tenth. The mean of the four FY25 quarters in the same
file is 29.68 / 40.31 / 16.90 / 13.11, which reproduces the 10-K. The 10-K itself:
`data/raw/regulatory/quantification/abnb_2025_10k.json` index 43, Geographic Mix (North America 158m, EMEA
215m, Latin America 90m, Asia Pacific 70m, total 533m), transcribed to `data/processed/adr/01_regional_annual.csv`
— 158/533 = 29.6%, 215/533 = 40.3%, 90/533 = 16.9%, 70/533 = 13.1%. A second tell that the constant is not
an annual share table: it sums to **100.1**, not 100.0. Stated in `nights_v2_design.md` §2.1 point 3 and §5,
and in §10 row 59.

**Decision.** **DEC-0032** ("E4 FY25 share label = 2Q26 quarterly").

**What changes if the FY25 shares were used.** **Unquantified, small.** The design does not re-run the index
on the 10-K weights and says why: the mislabel "affects the **cross-check** (§5), not the mechanism", and
re-weighting is outside that file's lane. What the design does quantify is the weight error itself: the
constant **overweights EMEA by about 1.3pp and underweights North America by about 1.3pp** relative to the
10-K (41.6 vs 40.3; 28.3 vs 29.6), with LatAm +1.0pp and APAC −0.8pp. On the direction: EMEA is the slower
of the two large regions in the letters' own buckets, so the mislabel is not obviously flattering to our
side. Nobody should quote a number for the size of it until E4 is re-run on the 10-K weights.

**Consequence.** The **base is untouched**: DEC-0029 moved the 3Q26 base to the mechanism (146.8m), and the
mechanism does not use `FY25_NIGHTS_SHARE` at all — it uses WS10's own share estimate 0.288 and its regional
buckets. The reviews-index reads (147.0 raw / 146.3 W2-corrected / 144.8 W1-corrected) are now cross-checks,
and they carry this defect. Anyone quoting the index read in the memo must say the regional weights are the
2Q26 quarterly shares, mislabelled FY25. The fix — re-running `E4`–`E6` on the 10-K weights — is a
cross-lane request, not a change made here.

---

## 4. The lap range in the pre-registration file: "0.9 to 1.8 points" against an admissible 0.70–0.88

**What the earlier artefact says.** `data/processed/overnight2/D/D1_prereg_thresholds.csv`, **row 5** (metric
"4Q26 nights guide issued 5 November"), `supports_hypothesis` cell: the guide implying 7.5% or below "is
consistent with both the global fee and cancellation lap that PR #32 omits ex-NA, **worth 0.9 to 1.8
points**, and with a cancellation tail from 1H26 cohorts".

**What is correct.** The admissible range for that lap is **0.70 to 0.88 points**.

**Evidence.** `data/processed/overnight2/D/D1_exna_4q26_gap.csv`, written by the **same script in the same
run** (`analysis/src/overnight2/D1_rnpl_cohort_scenarios.py`; receipt
`data/processed/pitch_model_v2/receipts/D1/receipt_D1_cohort.json`, max abs diff 0.0 on all 8 CSVs), all four
rows, column `pts_missing_from_4q26` and column `consistent_with_4q25_disclosure`:

| ex-NA share of the ex-NA bundle | points missing from 4Q26 | adjusted 4Q26 | level | consistent with the 4Q25 disclosure? |
|---|---:|---:|---:|---|
| 40% | **0.70** | 8.20% | 131.9m | yes |
| 50% | **0.88** | 8.03% | 131.7m | yes |
| 70% | 1.22 | 7.68% | 131.3m | **no** — implies a 4Q25 bundle of 2.6 to 3.1 points against "over 200 basis points" |
| 100% | 1.75 | 7.15% | 130.6m | **no** — same reason |

The two rows that generate the "0.9 to 1.8" span are exactly the two the gap file marks inadmissible. The
cap is management's own 4Q25 sentence (ledger **D014**, "over 200 basis points of growth in nights booked"):
in 4Q25 ex-NA RNPL was zero, so the ex-NA bundle that quarter was the fee and cancellation legs alone, and at
70% or 100% the implied 4Q25 bundle is 2.6–3.1 points, not "over 200 basis points" read as a number near 2.
`nights_v2_design.md` §2.3 states the conflict and names the gap file as governing; §10 row 58 carries it;
`final_nights.md` v1 §4.6 and §7.4 item 6 already flagged it as a live conflict.

**Decision.** **DEC-0032** ("D1_prereg_thresholds lap range 0.9-1.8 → 0.70-0.88").

**Consequence.** Two files from one folder disagreed by a factor of two on the size of the 4Q26 lap; the gap
file governs and the thresholds file is wrong. Nothing in the model moves — the adopted 4Q26 lap is the 45%
midpoint, **0.78 points**, inside 0.70–0.88, and `06_assumptions.csv`'s governing 1.649 ex-NA bundle at the
0.288 share gives **0.742** for the same leg (`nights_v2_design.md` §2.3; the whole 0.78-vs-0.742 spread is
0.05pp of 4Q26 growth, about 0.06m nights). What moves is what a reader of the pre-registration would
conclude about a 5 November guide: the omitted lap can support a guide implying ~8.0–8.2%, not one implying
7.1–8.0%. The CSV is another lane's artefact and has not been edited.

---

## 5. Provenance flag: ledger rows D014 and D032 are transcript mirrors — **resolved 18 Sep**

**What the earlier artefacts say.** The two sentences that size the product bundle, and therefore set every
lap in this line, are carried as verified quotes:

| ledger row | date | period | quote | `official_or_mirror` | source |
|---|---|---|---|---|---|
| **D014** | 2026-02-12 | 4Q25 | "In total, we estimate these three features delivered **over 200 basis points** of growth in nights booked and roughly 300 basis points of growth in GBV in Q4." (Ellie Mertz, 4Q25 call) | **mirror** | `data/raw/transcripts/web/4Q25.html`; `https://stockanalysis.com/stocks/abnb/transcripts/396495-q4-2025/`; accessed 2026-09-11 |
| **D032** | 2026-05-07 | 1Q26 | "In total, we estimate these three features delivered **approximately three points** of nights booked growth and approximately four points of GBV growth in Q1." (Ellie Mertz, 1Q26 call) | **mirror** | `data/raw/transcripts/web/1Q26.html`; `https://stockanalysis.com/stocks/abnb/transcripts/556160-q1-2026/`; accessed 2026-09-11 |

Both rows are `quote_verified = file` — verified against the mirrored HTML we hold, **not** against an
SEC-filed document or Airbnb's own IR transcript. All 60 rows live in
`data/processed/overnight2/D/rnpl_statement_ledger.csv`, built by
`analysis/src/overnight2/D0_rnpl_statement_ledger.py`.

**What is correct, and what is not yet known.** The provenance asymmetry is real and must be stated before a
judge finds it: **the dates are SEC-filed and the magnitudes are not.** Rows D012, D013, D024 and D060 —
which date the cancellation redesign and both fee tranches to October–December 2025 and describe them as
**global** — are `official_or_mirror = official`, sourced to `data/raw/letters/3Q25_d40503dex991.htm` and
`4Q25_d58192dex991.htm` with their SEC URLs. So is D031 ("roughly 20% of global GBV came from Reserve Now,
Pay Later bookings", 1Q26 letter), D042 (the ~100bp Middle East figure) and D052 (the 3Q26 guide). The two
rows that **size** the bundle, D014 and D032, are the two that are mirrors.

Whether either sentence also appears in an SEC-filed 8-K exhibit (some issuers furnish the prepared remarks
as an Ex-99 alongside the letter) was **not established in this repository** when this note was opened. Per
**DEC-0031** an X3 digger checked the EDGAR 8-K exhibits for the 4Q25 (12 Feb 2026) and 1Q26 (7 May 2026)
filings. It has reported.

**Verdict — filled 18 September 2026 from
`docs/pitch-model-v2/dossiers/X3_x3_bundle_sentences_provenance.md` (grade C).
Neither sentence exists in any SEC filing.**

| row | filing checked | accession / exhibit | sentence present in an SEC-filed exhibit? | verdict |
|---|---|---|---|---|
| **D014** (4Q25, "over 200 basis points") | 8-K, filed 2026-02-12 | **0001193125-26-048670**, **Exhibit 99.1 only** (the shareholder letter) | **no** — the 4Q25 letter is qualitative: "this feature contributed to the acceleration of bookings we saw in Q4". No basis-point figure. | **CONFIRMED not filed** |
| **D032** (1Q26, "approximately three points") | 8-K, filed 2026-05-07 | **0001193125-26-211816**, **Exhibit 99.1 only** (the shareholder letter) | **no** — the 1Q26 letter gives a **different** official metric: "roughly 20% of global GBV came from Reserve Now, Pay Later bookings", a **share**, not a growth contribution. | **CONFIRMED not filed** |

Three further findings from the same check. **No transcript exhibit was filed in either quarter** — neither
8-K carries an Ex-99.2 or any prepared-remarks exhibit, so there is no filed document in which either
sentence could appear. The **FY2025 10-K** and the **2Q26 10-Q** MD&A carry **no basis-point language** about
the bundle. The **1Q26 10-Q** (accession **0001559720-26-000014**) was **located but not read** — the one
gap in the check, and the reason the dossier grades itself **C**.

**Open follow-up:** read the 1Q26 10-Q (0001559720-26-000014) MD&A for any bundle-contribution language
before the memo freezes. It is the only filing in the window that has not been looked at, and it is the one
place a filed "approximately three points" could still turn up.

**Decision.** **DEC-0031** ("a digger checks EDGAR 8-K exhibits for the 4Q25 and 1Q26 bundle-contribution
statements (ledger D014 '>200bp', D032 '~3 points'); if not in a filing, the mirror provenance stays flagged
in the memo"). The condition has triggered: not in a filing, so the flag stays.

**Consequence — how the two sentences are cited from here on.** The citation changes and the numbers do not.

1. **Cite them as what they are: CFO statements on an earnings call, by date and speaker, sourced to the
   public IR webcast replay** — "Ellie Mertz, 4Q25 earnings call, 12 February 2026" and "Ellie Mertz, 1Q26
   earnings call, 7 May 2026" — **not** to a transcript mirror. `stockanalysis.com` is where we read them;
   it is not the source and must not be presented as one. Both are **marked for human verification against
   the replay** before the memo freezes.
2. **Quote the filed scale beside them.** The 1Q26 shareholder letter's "**roughly 20% of global GBV came
   from Reserve Now, Pay Later bookings**" (ledger **D031**, `official`) is the SEC-filed measure of how
   large RNPL is. It is a GBV share and not a growth contribution, so it does not substitute for D032 — it
   establishes that the feature is big enough for a three-point bundle to be plausible, and it is the number
   that carries a filing behind it.
3. **Everything downstream keeps the flag**: the fitted legs (+2.40 RNPL and +2.29 fee-plus-cancellation
   points of NA nights), the ex-NA bundle of 1.649 points backed out of D032's "approximately three points",
   the 4Q26 lap of −0.742, the 2027 lap terms, and the 4Q25 out-of-sample check that rules out the 70% and
   100% splits using D014.
4. **Say it before a judge does**, in the form `nights_v2_design.md` §8 uses: the dates carry the weight and
   they are SEC-filed; the magnitudes are unfiled call statements; and the shape survives if the bundle is 2
   points instead of 3 — that is the `global_bundle_pts` row of the design's §4.1 band, worth +0.45pp on
   4Q26 and +1.0pp on each of the 2H27 quarters, and the path still decelerates.

Not done here: `official_or_mirror` in `rnpl_statement_ledger.csv` still reads `mirror` for both rows, which
is now the wrong label in a second way — the sentences are not mirrored filings, they are unfiled call
statements. Re-labelling the ledger is another lane's artefact and is left as a request.
