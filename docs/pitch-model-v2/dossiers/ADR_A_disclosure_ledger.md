> Research survey by an autonomous Opus subagent on 21 Sep 2026 (overnight ADR session), read-only against the repo at HEAD 2a77a36; archived verbatim as provenance for docs/pitch-model-v2/lines/adr_v1_design.md. Model output, not a team decision.

# A — ADR disclosure ledger: what Airbnb management has actually said about the drivers of ADR

- **Date:** 2026-09-21 · **Repo:** `/Users/theomachado/Citadel-ABNB`, branch `theo/pitch-model-v2` (read-only; nothing in the repo was modified)
- **Purpose:** a dated, sourced record of management's own causal statements about ADR (= GBV / Nights and Seats Booked), so an ADR line can be built the way the nights line was: regional underlying growth + product bundle as management sized it + events, each lapped on its filed anniversary.
- **Definition of "filed":** an SEC-filed document — the 8-K Exhibit 99.1 shareholder letter, the 10-Q, the 10-K, or an Airbnb newsroom page (the ledger's `official` class). **"Transcript mirror"** = an earnings-call quote from a third-party transcript page. **Airbnb does not file its earnings-call transcript with the SEC in any form** — confirmed structurally: the 4Q25 8-K (accession 0001193125-26-048670) and 1Q26 8-K (0001193125-26-211816) each carry exactly one substantive exhibit, Ex-99.1 (the letter), plus page JPGs; no transcript exhibit (`docs/pitch-model-v2/dossiers/X3_x3_bundle_sentences_provenance.md` §3 step 2, §4).

## 0. Sourcing note — where the raw text came from, and one gap

- `data/raw/letters/*.htm` (the paths the guidance ledger cites) **is empty in this checkout** — `/Users/theomachado/Citadel-ABNB/data/raw/letters/` does not exist; the letters are gitignored (`.gitignore:28`, per `docs/pitch-model-v2/lines/nights_v2_design.md` §3.1). Raw letter/transcript text used below is the PDF-extraction cache at
  `/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/FX-ADR-R-model/public-data-2026-09-07/text/{YYYY}Q{N}_letter.txt` and `..._transcript.txt`, plus the on-disk filings `data/raw/regulatory/quantification/abnb_2025_10k.json` and `abnb_2026q2_10q.html`.
- **The PDF extraction inserts spurious spaces** ("grow th", "quar ter", "shif t", "ser vice", "Nor th"). Every quote below has been de-spaced for readability; the *words* are verbatim. Re-verify against the SEC HTML before any quote goes on a slide.
- **Gap: the 2Q25 shareholder letter text is not in the local cache** (only `2025Q2_transcript.txt`). 2Q25 numbers below come from `data/processed/overnight/02_kpi_panel_long.csv` rows 812–816, each carrying a short verbatim clause and `source_file = data/raw/letters/2Q25_d17531dex991.htm`, `source_verified = True`. **The 2Q25 global ADR driver sentence ("largely due to …") is therefore not reproduced here from raw text.** Flagged for human verification.

---

## 1. Per-quarter disclosed ADR facts, 1Q23 – 2Q26

Levels and computed y/y from `data/processed/overnight/02_kpi_panel_quarterly.csv` (rows 12–25; columns `adr_usd`, `adr_yoy_pct`, `adr_yoy_exfx_pct`, `fx_pts_adr`, `adr_yoy_na_pct`, `adr_yoy_emea_pct`, `adr_yoy_emea_exfx_pct`, `adr_yoy_latam_pct`, `adr_yoy_apac_pct`). Regional reported/ex-FX cross-checked against `data/processed/overnight/10_regional_panel_quarterly.csv` (rows 11–24) and `data/processed/adr/04_regional_quarterly_wide.csv` (rows 10–23).

**Identity convention (X1 §2):** `reported ADR y/y = ex-FX ADR y/y + adr_fx_pp`, denominator the prior-year quarter's ADR. `fx_pts_adr` is the *disclosed* FX effect = unrounded reported y/y minus the letter's whole-point ex-FX figure. The identity closes to within 0.042pp in every quarter (`analysis/src/predictive/03_nowcast_tests.py` L66; X1 §2a).

### 1.1 Global table

| Q | ADR $ | reported y/y (computed) | letter's word for it | ex-FX y/y (letter, whole pts) | FX pp | GBV y/y rep / ex-FX | nights y/y |
|---|---|---|---|---|---|---|---|
| 1Q23 | 168.43 | +0.21% | "flat compared to Q1 2022" | **+3%** | **−2.8** | 19 / 22 | 18.6 |
| 2Q23 | 166.01 | +1.39% | "a 1% increase" | **+2%** | **−0.6** | 13 / 13 | 11.0 |
| 3Q23 | 161.38 | +3.16% | "a 3% increase" | **"less than 1%"** (panel 0.5) | **+2.7** | 17 / 14 | 13.5 |
| 4Q23 | 156.73 | +2.57% | "a 3% increase" | **"less than 1%"** (panel 0.5) | **+2.1** | 15 / 13 | 12.0 |
| 1Q24 | 172.88 | +2.64% | "increasing 3%" | **+2%** | **+0.6** | 12 / — | 9.5 |
| 2Q24 | 169.53 | +2.12% | "increasing 2%" | **+3%** | **−0.9** | 11 / 12 | 8.7 |
| 3Q24 | 163.64 | +1.40% | "increasing 1%" | **+2%** | **−0.6** | 10 / 10 | 8.5 |
| 4Q24 | 158.13 | +0.89% | "increasing 1%" | **+2%** | **−1.1** | 13 / 15 | 12.4 |
| 1Q25 | 171.34 | −0.89% | "declining 1%" | **+1%** | **−1.9** | 7 / 9 | 7.9 |
| 2Q25 | 174.48 | +2.92% | *(letter text not in local cache)* | **+1%** | **+1.9** | 11 / 9 | 7.4 |
| 3Q25 | 171.29 | +4.67% | "increasing 5%" | **+2%** | **+2.7** | 14 / 12 | 8.8 |
| 4Q25 | 167.51 | +5.93% | "increasing 6%" | **+3%** | **+2.9** | 16 / 13 | 9.8 |
| 1Q26 | 186.82 | +9.03% | "increasing 9%" | **+4%** | **+5.0** | 19 / 13 | 9.2 |
| 2Q26 | 183.73 | +5.30% | "increasing 5%" | **+4%** | **+1.3** | 16 / 15 | 10.3 |

*Reconciliation of the letter's whole-point reported figure with the computed value: the letter rounds. 3Q25 "increasing 5%" against a computed +4.67%; 4Q25 "increasing 6%" against +5.93%. Use the computed value for the model and the letter's word for the quote.*

### 1.2 Regional ADR y/y (reported / ex-FX, as disclosed)

Blank = not disclosed that quarter. `02_disclosure_changes.csv` row 12: *"Regional ADR y/y | 2Q23 start | NA/EMEA from 2Q23; all four regions with ex-FX from 1Q25 | letters"* — so **only 1Q25 onward has a complete four-region reported+ex-FX set**. In 1Q24–3Q24 the NA/EMEA ex-FX figures are stated as *"excluding the impact of FX **and mix shift**"* — a different, narrower object than the global ex-FX line, and it must not be chained to it.

| Q | NA rep | NA ex-FX | EMEA rep | EMEA ex-FX | LatAm rep | LatAm ex-FX | APAC rep | APAC ex-FX |
|---|---|---|---|---|---|---|---|---|
| 1Q23 | | | +8 | | | | | |
| 2Q23 | −1 | | +8 | | | | | |
| 3Q23 | −1 | | | +6 | | | | |
| 4Q23 | 0 | −2 *(ex-FX **and mix**)* | | +6 | | | | |
| 1Q24 | +3 | 0 *(ex-FX and mix)* | +7 | +4 *(ex-FX and mix)* | | | | |
| 2Q24 | +4 | +1 *(ex-FX and mix)* | +4 | +3 *(ex-FX and mix)* | | | | |
| 3Q24 | +3 | +1 *(ex-FX and mix)* | +6 | +3 *(ex-FX and mix)* | | | | |
| 4Q24 | +3 | | +6 | +6 | −5 | +4 | +1 | +2 |
| 1Q25 | +2 | +3 | +2 | +4 | −7 | +2 | −1 | +3 |
| 2Q25 | +3 | | +9 | +3 | −3 | +2 | +2 | +1 |
| 3Q25 | +5 | | +10 | +4 | +4 | +3 | +2 | +3 |
| 4Q25 | +5 | | +12 | +4 | +9 | +3 | +2 | +2 |
| 1Q26 | +7 | | +15 | +4 | +10 | +3 | +6 | +2 |
| 2Q26 | +7 | | +7 | +5 | +9 | +2 | +1 | **not given** |

**Two data cautions.** (a) **NA ex-FX is not disclosed from 2Q25 onward** — the NA paragraph gives reported only and names the driver in words. `data/processed/adr/04_regional_quarterly_wide.csv` col `adr_yoy_exfx_na_pct` shows 3.33 (2Q25), 5.05 (3Q25), 4.78 (4Q25), 6.30 (1Q26), 6.75 (2Q26) under `basis_adr_na = disclosed-chained` — **these are constructed, not disclosed.** (b) 2Q26 APAC ex-FX: the letter gives none; `04_regional_quarterly_wide.csv` row 23 carries −1.3509 for `adr_yoy_exfx_apac_pct` with basis `disclosed-chained`, while `10_regional_panel_quarterly.csv` row 24 leaves `apac_adr_yoy_exfx_pct` **blank**. **Contradiction between the two repo files; the blank is right, the −1.35 is a reconstruction.**

### 1.3 The driver sentence, verbatim, quarter by quarter

All from the 8-K Ex-99.1 shareholder letter → **filed**. Paragraph ids are in the PDF-text cache.

**1Q23 (13 May 2023, `2023Q1_letter.txt` p89):**
> "ADR was $168 in Q1 2023, flat compared to Q1 2022. Excluding the impact of FX, ADR in Q1 2023 increased 3% from Q1 2022. **ADR remained stable on a year-over-year basis as price appreciation was offset by the impact of foreign exchange, willingness to pay, and mix shift into urban and other types of bookings, which tend to carry lower ADR.** On an FX-neutral basis, Q1 2023 ADR was flat to up across all regions year-over-year."

**2Q23 (3 Aug 2023, p97):**
> "ADR was $166 in Q2 2023, representing a 1% increase from Q2 2022. Excluding the impact of FX, ADR in Q2 2023 increased 2%… **ADR remained stable on a year-over-year basis as increases in prices listed by Hosts were offset by guests' willingness to pay and mix shift into urban and certain geos, which tend to carry lower ADR.** On an FX-neutral basis, Q2 2023 ADR was down in North America and Latin America, but up in EMEA and Asia Pacific year-over-year. **In North America, we saw a decrease in available prices of 2% in Q2 2023 compared to Q2 2022 as Hosts reduced prices.**"

**3Q23 (1 Nov 2023, p86):**
> "ADR was $161 in Q3 2023, representing a 3% increase from Q3 2022. Excluding the impact of FX, ADR in Q3 2023 increased **less than 1%** from Q3 2022 **partially due to mix shift**."

**4Q23 (13 Feb 2024, p82 and p39):**
> "ADR was $157 in Q4 2023, representing a 3% increase… Excluding the impact of FX, ADR in Q4 2023 increased less than 1% from Q4 2022 **partially due to mix shift**."
> (p39, affordability) "Since launching these features, 1.4 million Hosts have used Similar Listings… since launching **Total Price Display** in early 2023, we've seen nearly **300,000 listings remove or lower their cleaning fees**. By the end of the year, **nearly 40% of our active listings charged no cleaning fee at all**. Excluding the impact of FX, year-over-year growth in global ADR remained relatively stable the past three quarters… **while the average nightly price of a one-bedroom listing on Airbnb in December was $114, down 2% from the prior-year period, hotel prices rose 7% to $149**."

**1Q24 (8 May 2024, p93; NA p80; EMEA p81):**
> "ADR was $173 in Q1 2024, increasing 3%… Excluding the impact of FX, ADR in Q1 2024 increased across all regions, representing a year-over-year increase of 2% **largely due to price appreciation**."
> NA: "ADR in North America increased 3%… but was **flat year-over-year when excluding the impact of FX and mix shift**. **Growth in short-term stays and entire homes outpaced long-term stays and Airbnb rooms, respectively, driving the mix shift.**" Also: "**nights booked for groups of over five people increased 15%** compared to Q1 2023 — the fastest growing segment in the region for the fourth consecutive quarter."

**2Q24 (6 Aug 2024, p71; NA p65):**
> "ADR was $170 in Q2 2024, increasing 2%… Excluding the impact of FX, ADR in Q2 2024 increased 3% and was higher across all regions, **largely due to price appreciation and mix shift**."
> NA: "nights booked for groups of over five people increased 16%… **the average number of guests on a booking in North America is increasing. As a result, nights booked on a per-guest basis grew four percentage points faster year-over-year than nights booked in North America in Q2.** ADR in North America increased 4%… or 1% excluding the impact of FX and mix shift."

**3Q24 (7 Nov 2024, p90; NA p83):**
> "ADR was $164 in Q3 2024, increasing 1%… Excluding the impact of FX, ADR in Q3 2024 increased 2% and was flat to up across all regions, **largely due to price appreciation and mix shift**."
> NA: "…or 1% excluding the impact of FX and mix shift. **Growth in short-term stays and entire homes continued to outpace long-term stays (trips of 28 days or more) and Airbnb rooms**… despite the relative outperformance of short-term stays, **long-term stays comprised 23% of gross nights booked in North America** during Q3 2024, largely unchanged from the prior-year period."

**4Q24 (13 Feb 2025, p76; NA p68/70; EMEA p71; LatAm p72; APAC p74):**
> "ADR was $158 in Q4 2024, increasing 1%… Excluding the impact of FX, ADR in Q4 2024 increased 2% and was up across all regions, **largely due to price appreciation**."
> NA: "ADR in North America increased 3% in Q4 2024… **driven by price appreciation and mix shift.** Growth in short-term stays and entire homes continued to outpace long-term stays (trips of 28 days or more) and Airbnb rooms…"
> EMEA: "ADR increased 6% **on a reported and FX-neutral basis**… **driven by continued price appreciation and mix shift**."
> LatAm: "ADR declined 5%… **largely due to FX**. On an FX-neutral basis, ADR increased 4%."
> APAC: "ADR increased 1%… **largely due to price appreciation**. On an FX-neutral basis, ADR increased 2%."

**1Q25 (1 May 2025, p47; NA p51/53; EMEA p55; LatAm p56; APAC p58):**
> "…The increase in Nights and Experiences Booked was partially offset by a slight decline in ADR, **which was impacted by FX headwinds** during the quarter. ADR was $171 in Q1 2025, declining 1%… Excluding the impact of FX, ADR in Q1 2025 increased 1% and was up across all regions, **largely due to price appreciation**."
> NA: "ADR in North America increased 2%… (or 3% ex-FX), **primarily driven by mix shift.** Growth in short-term stays and entire homes continued to outpace long-term stays… and Airbnb rooms…"
> EMEA: "+2% (or 4% ex-FX), **primarily driven by continued price appreciation and mix shift**." LatAm: "−7%… **primarily driven by FX**. On an ex-FX basis, ADR increased 2%… **due to price appreciation**." APAC: "−1%… **primarily driven by FX**. On an ex-FX basis, +3%… **due to price appreciation**."

**2Q25 (6 Aug 2025)** — letter text not in local cache. Verified clauses only (`02_kpi_panel_long.csv` rows 812–816, `source_file = data/raw/letters/2Q25_d17531dex991.htm`): *"Excluding the impact of FX, ADR in Q2 2025 increased 1%"*; *"ADR in North America increased 3% in Q2 2025"*; *"ADR in EMEA increased 9% in Q2 2025"*; *"ADR in Latin America declined 3% in Q2 2025"*; *"ADR in Asia Pacific increased 2% in Q2 2025"*. **The global driver clause for 2Q25 is a hole in this ledger.**

**3Q25 (6 Nov 2025, p66; NA p70/72; EMEA p74; LatAm p75; APAC p77):**
> "…The year-over-year growth in GBV was driven by the continued growth of Nights and Seats Booked, as well as an increase in ADR, **which benefited from FX tailwinds** during the quarter. ADR was $171 in Q3 2025, increasing 5%… Excluding the impact of FX, ADR in Q3 2025 increased 2% and was up across all regions, **largely due to price appreciation**."
> NA: "ADR in North America increased 5%… **primarily driven by mix shift. Growth in short-term stays and entire homes continued to outpace long-term stays (trips of 28 days or more) and private rooms**…" *(note: "private rooms" replaces "Airbnb rooms" from this letter on)*
> EMEA: "+10%… **primarily driven by FX**. On an ex-FX basis, +4%… **primarily due to price appreciation**." LatAm: "+4%… **primarily driven by price appreciation and FX**; ex-FX +3%." APAC: "+2%… **primarily driven by price appreciation**; ex-FX +3%."

**4Q25 (12 Feb 2026, p57; NA p60; EMEA p61; LatAm p62; APAC p63):**
> "…an increase in ADR, **which benefited from FX tailwinds** during the quarter. ADR was $168 in Q4 2025, increasing 6%… Excluding the impact of FX, ADR in Q4 2025 increased 3% year-over-year and was up across all regions, **largely due to price appreciation**."
> NA: "ADR in North America increased 5%… **primarily driven by mix shift. Growth in short-term stays and entire homes, particularly listings with 4 or more bedrooms, continued to outpace long-term stays (trips of 28 days or more) and private rooms**, respectively, helping to drive the mix shift." **← first appearance of "4 or more bedrooms" in a filed ADR driver sentence.**
> EMEA: "+12%… **primarily driven by FX**; ex-FX +4%, **primarily due to price appreciation**." LatAm: "+9%… **primarily driven by FX and price appreciation**; ex-FX +3%." APAC: "+2%… **primarily driven by price appreciation**; ex-FX also +2%."

**1Q26 (7 May 2026, p59; NA p62; EMEA p64; LatAm p65; APAC p66):**
> "ADR was $187 in Q1 2026, increasing 9%… **benefiting from FX tailwinds as well as continued strong ADR growth in North America.** Excluding the impact of FX, ADR in Q1 2026 increased 4% year-over-year and was up across all regions, **largely due to price appreciation**."
> NA: "ADR in North America increased 7%… **driven by both mix shift and price appreciation. Growth in short-term stays and entire homes, particularly listings with 4 or more bedrooms, continued to outpace long-term stays (trips of 28 days or more) and private rooms**, helping to drive the mix shift."
> EMEA: "+15%… **primarily driven by FX**; ex-FX +4%." LatAm: "+10%… **primarily driven by FX**; ex-FX +3%." APAC: "+6%… **primarily driven by FX**; ex-FX +2%."

**2Q26 (6 Aug 2026, p94; NA p99; EMEA p100; LatAm p101; APAC p102; bedroom nights p95):**
> "ADR was $184 in Q2 2026, increasing 5% compared to Q2 2025. On an ex-FX basis, ADR in Q2 2026 increased 4% year-over-year and was up across all regions — **particularly North America and EMEA — due to price appreciation and mix. Specifically, in Q2 2026, we saw entire homes, especially listings with four or more bedrooms continue to grow the fastest.**"
> NA: "+7%… **driven by both price appreciation and mix shift.** Growth in short-term stays and entire homes, particularly listings with four or more bedrooms, continued to outpace long-term stays… and private rooms, **extending a mix-shift trend we have now seen for over a year.**"
> EMEA: "+7%… ex-FX +5%, **primarily driven by price appreciation**." LatAm: "+9%… **primarily driven by FX**; ex-FX +2%." APAC: "+1%" **(no ex-FX given)**.
> **New filed metric — the single best direct size-mix read:** "while Nights and Seats Booked grew 10% year-over-year in Q2 2026, **Bedroom Nights Booked — nights booked multiplied by bedroom count — grew over 12%**, continuing a multi-year pattern. In fact, over the trailing twelve months through Q2 2026, guests booked **more than 1 billion bedroom nights**." (`02_disclosure_changes.csv` row 17: *"Bedroom Nights Booked | 2Q26 start | new metric (nights x bedrooms) +12% vs nights +10%"*; `02_kpi_panel_quarterly.csv` col `bedroom_nights_yoy_pct` = 12.0 at 2Q26, blank everywhere else.)

### 1.4 The forward ADR sentence (the guide), 4Q22 print → 2Q26 print

From `data/processed/overnight/02_guidance_ledger.csv`, rows with `metric = adr_yoy_pct`. All **filed** (8-K Ex-99.1). `actual` and `outcome` are the file's own scoring.

| print | for | guide quote (letter, Outlook) | type | actual | outcome |
|---|---|---|---|---|---|
| 4Q22 (2023-02-14) | 1Q23 | "In Q1 2023, we anticipate slightly lower ADR than we had in Q1 2022" | directional, below 0 | +0.21 | **not_met** |
| 4Q22 (2023-02-14) | FY23 | "For the remainder of the year, we expect ADR will face increasing downward pressure from **mix shift**, as well as **new and improved pricing and discounting** [tools]" | qualitative | — | not_scoreable |
| 1Q23 (2023-05-09) | 2Q23 | "we anticipate a slightly lower ADR in Q2 2023 than Q2 2022 **driven by mix shifts and the introduction of new Host pricing tools as part of our 2023 Summer Release**" | directional, below 0 | +1.39 | **not_met** (wrong sign) |
| 2Q23 (2023-08-03) | 3Q23 | "While our **new Host pricing tools have had a moderating effect on ADR**, we expect **upward pressure on ADR from FX rates and listing type mix shift** to outweigh their impact and drive a year-over-year increase in ADR in Q3 2023" | floor 0 | +3.16 | met |
| 3Q23 (2023-11-01) | 4Q23 | "we expect ADR in Q4 2023 to be stable to slightly up" | floor −0.5 | +2.57 | met |
| 4Q23 (2024-02-13) | 1Q24 | "We expect ADR for the quarter to be flat to slightly up compared to Q1 2023" | floor −0.5 | +2.64 | met |
| 1Q24 (2024-05-08) | 2Q24 | "estimate that ADR for the quarter will be modestly up… **due to mix shift, partially offset by the impact of FX rate changes**" | floor 0 | +2.12 | met |
| 2Q24 (2024-08-06) | 3Q24 | "we expect ADR to increase modestly on a year-over-year basis in Q3 2024" | floor 0 | +1.40 | met |
| 3Q24 (2024-11-07) | 4Q24 | "we expect ADR to increase modestly… **driven by continued demand for larger and higher priced listings, as well as a small benefit from foreign exchange**" | floor 0 | +0.89 | met |
| 4Q24 (2025-02-13) | 1Q25 | "we expect ADR to decline slightly… **largely driven by FX headwinds. Excluding the impact of FX, we would have anticipated a slight year-over-year increase in ADR.**" | ceiling 0 | −0.89 | met |
| 1Q25 (2025-05-01) | 2Q25 | "In Q2 2025, we expect ADR to be approximately flat year-over-year" | point 0 | +2.92 | **beat** |
| 2Q25 (2025-08-06) | 3Q25 | "In Q3 2025, we expect ADR to increase modestly… **primarily driven by FX**" | floor 0 | +4.67 | met |
| 3Q25 (2025-11-06) | 4Q25 | "We anticipate our GBV to benefit from a modest increase in ADR, **primarily due to price appreciation and FX**" | floor 0 | +5.93 | met |
| 4Q25 (2026-02-12) | 1Q26 | "We expect GBV to increase in the low teens… driven by high-single-digit growth in Nights and Seats Booked and **a moderate increase in ADR due to price appreciation and FX**" | — | +9.03 | — |
| 1Q26 (2026-05-07) | 2Q26 | "In Q2 2026, we expect GBV to increase in the low double digits… driven by growth in Nights and Seats Booked and a moderate increase in ADR. **We expect the FX tailwind to ADR to be significantly lower in Q2 2026 than in Q1.**" | directional, below 8.0 | +5.30 | met |
| 2Q26 (2026-08-06) | **3Q26** | "We expect year-over-year GBV growth to be in the mid teens, driven by low double-digit growth in Nights and Seats Booked and **a moderate increase in ADR due to mix shift and price appreciation**" | floor 0 | pending | **pending** |

**The 3Q26 tell (X1 §2, primary source):** the 3Q26 ADR guide names **mix shift and price appreciation and does not name FX at all** — the first ADR guide since 1Q25 in which FX is absent. In the same letter the *revenue* guide names "an approximate three percentage point FX tailwind after factoring in our hedging program." Management drops FX from the ADR sentence while keeping it in the revenue sentence in the same paragraph block. That is a filed, qualitative statement that 3Q26 ADR-FX is near zero.

**Multi-year ADR claims management got wrong** (`data/processed/overnight/03_forward_claims.csv`) — useful as a credibility exhibit, not as a model input: C010 (2Q21, Stephenson, "we will see ADRs moderate… purely as part of mix") **missed**; C032 (1Q23, Stephenson, "full year… growth in ADR should be… down in that kind of mid-single-digit range") **missed** (FY23 was +1.8%); C033 (1Q23, Chesky, "all the supply coming on the market will keep prices from going up") **missed**; C068 (3Q25, Chesky, "as we get more supply, prices will come down") **missed** — ADR then rose 5.9% in 4Q25 and 9.0% in 1Q26.

---

## 2. Dated ledger of ADR-relevant product / policy events, and management's own sizing

Source column: **FILED** = SEC 8-K Ex-99.1 letter, 10-Q, 10-K, or Airbnb newsroom. **MIRROR** = earnings-call transcript only. Ledger ids are rows of `data/processed/overnight2/D/rnpl_statement_ledger.csv` (61 rows incl. header; row numbers given).

| date | event | what was said, verbatim | ADR relevance | source |
|---|---|---|---|---|
| 2022-12 | Total-price display toggle live; search ranking begins weighting total price | 4Q22 letter; `06_fee_timeline.csv` row 7 | lowers displayed/effective nightly price on some listings | FILED |
| 2023-05 | 2023 Summer Release: Host pricing/discount tools, Similar Listings, Airbnb Rooms | 2Q23 letter: "our **new Host pricing tools have had a moderating effect on ADR** in the quarter" | management's only *named* downward product driver of ADR | FILED |
| 2024-02 | ~300k listings removed/lowered cleaning fees; "**nearly 40% of our active listings charged no cleaning fee at all**" | 4Q23 letter p39 | cleaning fees are **inside GBV**, so this is a direct ADR drag | FILED |
| **2024-Q2** | **Additional service fee amount for cross-currency bookings begins** | 4Q24 letter p100 / 1Q25 letter p77: "During Q2 2024, we began charging an additional service fee amount for cross-currency bookings. The change does not affect the majority of our guests as **cross-currency transactions comprise approximately 20% of our GBV**." | a *guest service fee* is inside GBV ⇒ mechanically lifts ADR on ~20% of GBV. **Management has never sized its ADR effect** — they discuss it only in take-rate/revenue terms. | FILED |
| 2025-04-21 | Total price display becomes the **global default**, not a toggle | `06_fee_timeline.csv` row 15, news.airbnb.com | | FILED |
| **2025-08 (US launch)** | **Reserve Now, Pay Later (RNPL), US domestic, eligible listings on moderate/flexible policies** | D001/D002 (2025-08-14 newsroom); D008 (3Q25 letter): "In August, we launched our Reserve Now, Pay Later payment option within the U.S…. helped drive the acceleration of Nights and Seats Booked in North America during Q3 2025."; D004 (call): "we launched it at the beginning of Q3" | the US ADR leg starts here; **anniversary is 3Q26** | D001/D002/D008 FILED; D004 MIRROR |
| **2025-10** | **Cancellation-policy redesign, global** | D060 (4Q25 letter): "**In October**, we announced new cancellation policies… Hosts can now offer free cancellation up to 14 days before check-in under a new Limited policy."; D012 (3Q25 letter) gives the parameters (14 days / 24 hours / 7 days / 28 nights), **scope global** | one of the three bundle features | FILED |
| **2025-10-27 (tranche 1) / 2025-12 (step)** | **Single 15.5% service fee — PMS/API hosts migrated off the split fee** | D013 (3Q25 letter): "In October, we took steps to simplify our fee structure…"; D024 (4Q25 letter): "We began migrating property management software ('PMS') hosts on our split fee structure (where hosts paid a 3% fee and guests paid a separate service fee) to a **15.5% single service fee**. Additionally, **most non-PMS hosts… are now subject to the 15.5% fee as of December**." | **two dated tranches inside 4Q25, not one.** Hosts "are able to adjust their prices to maintain the same net earnings" ⇒ a payout-neutral reprice raises the listed nightly rate | FILED |
| 2026-02-12 | RNPL take-up | D022 (4Q25 letter): "After a strong U.S. launch — with **over 70% adoption by eligible bookings*** — and testing in other markets, we're rolling it out to more guests in 2026." (footnote: based on global GBV in Q4 2025) | **a different statistic** from the 3Q25 call's "about 70% of people that we offer… take us up" (D005, MIRROR). The ledger warns the two must not be chained. | D022 FILED; D005 MIRROR |
| **2026-02-17** | **RNPL global** | D025 (newsroom): "Reserve Now, Pay Later is now available to guests **globally** for domestic and international trips" — excluding BRL/INR/TRY payers (D027, 2026-02-23) | ex-NA ADR leg starts; **anniversary is 1Q27** | FILED |
| 2026-02-18 / 02-23 / 03-04 | RNPL UK / Australia / Canada | D026, D028, D029 (newsroom) | | FILED |
| 2026-06-22 → 2026-10-13 | **Single-fee tranche 2** (UK-resident hosts 22 Jun; non-EEA deadline 15 Sep 2026; **EEA/CH deadline 13 Oct 2026**; complete by year-end) | 2Q26 letter: "In July, we announced plans to migrate **most of the remaining hosts** to a single 15.5% service fee, with migration expected to be completed this year." Deadline dates are from `research/notes/adrv3/K_residual-decomposition-fee-migration.md` §2.6/§K1, sourced to the Guesty notice + letters | **the reprice does not lap in 4Q26 — it peaks there** (K point 5) | letter FILED; exact deadline dates: vendor notice, **team-sourced** |
| 2026-07 | RNPL eligibility expanded | D044 (2Q26 call): "Given the strong results that it's delivered, **in July, we expanded the types of bookings eligible** for Reserve Now, Pay Later." | | MIRROR |
| 2026-Q2 | Cancellation policies again | D048 (2Q26 letter): "We migrated eligible listings from **Strict to Firm** cancellation policies, helping hosts attract more bookings." | | FILED |
| 2025-05 → | Airbnb Services and reimagined Experiences (seats enter the KPI) | 3Q25 letter; 2Q26 letter: "increasing Airbnb Experiences supply by nearly **80% year-over-year** in Q2 2026" | **seats dilute the ADR denominator**: ADR = GBV / (nights **+ seats**). Management has never sized the dilution. Repo's assumed term: −0.48pp in 3Q26 (`D4_d4_adr.md`, labelled *assumed*) | FILED (events); dilution size = **team assumption** |

### 2.1 Management's quantification of the bundle — and its provenance

**This is the one place where management gave numbers that imply an ADR contribution, and both are transcript-only.**

| date | period | statement | implied ADR contribution | ledger row | provenance |
|---|---|---|---|---|---|
| **2026-02-12** (4Q25 call, Mertz) | 4Q25 | "In total, we estimate these three features delivered **over 200 basis points of growth in nights booked and roughly 300 basis points of growth in GBV in Q4**." | **≈ +1.0pp of ADR** (GBV-minus-nights gap) | **D014** (row 15) | **MIRROR only** |
| **2026-05-07** (1Q26 call, Mertz) | 1Q26 | "In total, we estimate these three features delivered **approximately three points of nights booked growth and approximately four points of GBV growth in Q1**." | **≈ +1.0pp of ADR** | **D032** (row 33) | **MIRROR only** |
| 2026-08-06 (2Q26 call, Mertz) | 2Q26 | "First, we continue to see Reserve Now, Pay Later benefit the business. It drove more bookings, longer booking lead times, and **contributed to the increase in ADR**." **No figure.** | not sized | **D045** (row 46) | MIRROR |

The three features are named (D015, 4Q25 call): "**the launch of Reserve Now, Pay Later; updates to our cancellation policies; and the beginning of our migration to a simplified fee structure**." **No per-feature split has ever been disclosed for any quarter** (D015 note).

**Provenance verdict (X3 §3, the digger output DEC-0031 asked for):** the 4Q25 and 1Q26 8-Ks each carry Exhibit 99.1 only. A full-text search of both letters for "basis points", "points of", and "these three features delivered" returns **nothing**. The FY2025 10-K's only "basis point" is interest-rate risk on the investment portfolio. The 2Q26 10-Q MD&A is qualitative. **The magnitudes exist only on the calls.** The one filing that was not directly checked is the 1Q26 10-Q, accession **0001559720-26-000014** — X3 §8 flags it as the open lead.

**What IS filed in place of a magnitude:**
- **D031 (1Q26 letter, FILED):** "in Q1, **roughly 20% of global GBV** came from Reserve Now, Pay Later bookings." This is a **GBV share, not a growth contribution, and not a nights share.** Converting it needs an RNPL-to-non-RNPL ADR ratio that has never been disclosed, and management has said RNPL's mix skews to larger, higher-priced homes, so the GBV share **overstates** the nights share.
- **D043 (2Q26 call, MIRROR):** "over 20% of our total GBV was booked using this flexible payment option." "Over 20%" against "roughly 20%" is **not a measurable increase**.
- **2Q26 10-Q MD&A, FILED, 6 Aug 2026** (`data/raw/regulatory/quantification/abnb_2026q2_10q.html`, Key Business Metrics → GBV): *"the increase in GBV… was primarily due to an increase in Nights and Seats Booked and ADR… **The increase in ADR was driven in part by the continued adoption of RNPL.**"* **This is the only SEC-filed sentence that names RNPL as a driver of ADR.** Qualitative, no points.
- **FY2025 10-K, FILED:** *"We saw a **3% increase in ADR in 2025** compared to the prior year, **primarily due to higher ADR in EMEA, which increased by 8%**."* Plus the filed size series: *"Our total Company **average nights per booking**, excluding experiences and services, was **3.7 in 2025 compared to 3.8 in 2024**. Average nights per booking in 2025 was **4.1 for North America, 3.8 for EMEA, 3.6 for Latin America, and 3.3 for Asia Pacific**."*

### 2.2 The mix mechanism management names, in its own words (all FILED)

- **"Larger / bigger homes":** 4Q25 and 1Q26 letters, NA paragraph — "entire homes, **particularly listings with 4 or more bedrooms**"; 2Q26 letter, global ADR paragraph — "we saw **entire homes, especially listings with four or more bedrooms continue to grow the fastest**"; 2Q26 NA — "**extending a mix-shift trend we have now seen for over a year**."
- **The recurring NA mix formula, unchanged 1Q24 → 2Q26:** "Growth in **short-term stays and entire homes** … outpaced **long-term stays (trips of 28 days or more)** and **Airbnb rooms** [→ "private rooms" from 3Q25], respectively, helping to drive the mix shift."
- **Group / party size:** 1Q24 "nights booked for groups of over five people increased 15%… the fastest growing segment in the region for the fourth consecutive quarter"; 2Q24 "+16%… fifth consecutive quarter" and "nights booked on a **per-guest basis grew four percentage points faster** year-over-year than nights booked in North America in Q2."
- **Bedroom Nights Booked (2Q26, new):** nights × bedrooms **+12%** vs nights +10% ⇒ **~2pp of size mix, measured by the company itself**.
- **RNPL → larger homes (MIRROR, D016, 4Q25 call):** "Reserve Now, Pay Later… **led to longer booking lead times and a mix shift towards larger entire homes, especially those with four or more bedrooms, contributing to the increase in ADR.**" Direction disclosed; the ratio is not.
- **Long-term-stay share:** disclosed 1Q21–1Q24 only (24% → 17%); from 2Q24 only the qualitative "short-term outpaced long-term" (`02_disclosure_changes.csv` row 10). NA-specific: 23% of NA gross nights in 3Q24, "largely unchanged" (3Q24 letter).

---

## 3. FX on ADR vs FX on revenue, and the hedging program

**Three distinct objects. The model must not mix them.**

1. **The ADR FX effect is a contemporaneous, gross-of-hedging translation restatement.** GBV — and therefore ADR — is a **booking-quarter** metric: FY2025 10-K, *"**The entire amount of a booking is reflected in GBV during the quarter in which booking occurs**, whether the guest pays the entire amount of the booking upfront or elects to use our Pay Less Upfront program"* and *"**Revenue from the booking is recognized upon check-in; accordingly, GBV is a leading indicator of revenue.**"* So ADR carries **this quarter's bookings at this quarter's currencies**.
2. **Constant-currency method (prior-period rates), letters only.** The shareholder letters' Constant Currency section (every letter, e.g. 1Q23 p163, 3Q23 p171) covers *"revenue, GBV, net income (loss), Adjusted EBITDA, **and ADR**"* and states the method: *"**We calculate the percentage change in constant currency by determining the change in the current period over the prior comparable period where current period foreign currency amounts are translated using the exchange rates of the comparative period.**"* → **prior-period rates.** **The 10-K and the 10-Q Constant Currency sections cover REVENUE ONLY** (verified verbatim in `abnb_2025_10k.json` and `abnb_2026q2_10q.html`: *"we disclose the percentage change in our current period **revenue**… using constant currencies"*). **So the ex-FX ADR figure is a shareholder-letter disclosure, not a 10-K/10-Q one.**
3. **Hedges are designated against REVENUE ONLY, never GBV or ADR.** FY2025 10-K: *"To protect **revenue** from fluctuations in foreign currency exchange rates, the Company may enter into forward contracts, option contracts, or other instruments, and may designate these instruments as cash flow hedges. **In the first quarter of 2023**, the Company initiated a foreign exchange cash flow hedging program to minimize the effects of foreign currency fluctuations on **future revenue**. The Company generally hedges portions of its forecasted foreign currency exposure associated with **revenue, typically for up to 18 months**."* Identical language in the 2Q26 10-Q. Risk-factor version (10-K): *"We utilize a foreign exchange cash flow hedging program to reduce the impact of currency fluctuations on our **revenue**. However, hedging may not fully mitigate losses…"*
   - Consequence (X1 §2, §5): **the letters' ex-FX ADR sentence is a pure translation restatement, gross of hedging; the revenue-FX sentence is stated after hedging.** They are not comparable and must not be swapped.
   - `02_disclosure_changes.csv` row 24: *"Hedging language in revenue guide | 2Q25 start | 'after factoring in our hedging program' appears from 2Q25 | letters"*.
   - 2Q26 letter, 3Q26 revenue guide (FILED): *"representing year-over-year growth of 15% to 17%, **inclusive of an approximate three percentage point FX tailwind after factoring in our hedging program**."* ← **a revenue number, after hedging.** In the same letter the 3Q26 **ADR** sentence names only "mix shift and price appreciation."
   - 4Q25 call (MIRROR, Mertz): "the realized tailwind of FX in Q1 will be quite strong at **nearly 3 percentage points**" — also a revenue statement.
   - 2Q25 call (MIRROR, Mertz), 3Q25 guide: "This includes **minimal impact for foreign exchange after factoring in our hedges**. …and for ADR to increase modestly year-over-year, **primarily driven by FX**." **Same quarter, same speaker: FX is "minimal" for revenue after hedges and the "primary" driver of ADR.** That pair is the cleanest single proof that the two FX objects differ.

**The disclosed ADR-FX series, every quarter it exists** (17 quarters, 2Q22–2Q26; `docs/pitch-model-v2/dossiers/X1_x1_adr_fx_reconciliation.md` §2a, `X1_disclosed_vs_objects.csv`): −5.6, −7.1, −5.5, −2.8, −0.6, +2.7, +2.1, +0.6, −0.9, −0.6, −1.1, −1.9, +1.9, +2.7, +2.9, +5.0, **+1.3 (2Q26)**.

**The repo's own FX dispute, resolved — do not repeat it.** X1 (18 Sep 2026) establishes that D5's `point_phi_adrfx_pp` (+2.89pp for 3Q26) is **not an ADR quantity**: it puts zero weight on the quarter's own currency basket and two-thirds on the prior quarter's, i.e. it is a **revenue**-FX construction. Scored against the 17 disclosed ADR-FX points it has RMSE **2.20pp**, wrong sign in 4 of 17. The ADR line carries **−0.43pp (3Q26), +0.15pp (4Q26)** — the adrv3 N midpoint, RMSE **0.406pp** on all 17 and 0.332pp on 1Q24–2Q26. X1 §6: adopting D5's number would put 3Q26 ADR at $182.56 vs Street $177.06 — "a 3.1% variant view on ADR created entirely by a labelling error."
**Also from X1 §5:** "Do not add any FX pp on top of the GBV-lag dollar path" — the kernel's base is lagged GBV, which already carries booking-date FX.

---

## 4. What a mechanism model may legitimately use

### 4.1 FILED — quotable as management's own disclosure

1. **The ADR identity and its FX split, every quarter 2Q22–2Q26.** Reported ADR y/y, ex-FX ADR y/y (whole points), and the gap as the FX effect. Letters only; prior-period-rate method; gross of hedging.
2. **The four-region ADR y/y, reported, from 2Q23 (NA/EMEA) and from 4Q24 (all four); ex-FX for all four from 1Q25.** With the caveat that NA ex-FX stops being given after 1Q25 and that 1Q24–3Q24 "ex-FX **and mix**" is a narrower object.
3. **The driver vocabulary and its sequence:** *price appreciation* (global ex-FX driver in every letter from 1Q24), *mix shift* (NA's primary driver in 1Q25, 3Q25, 4Q25; joint with price from 4Q24, 1Q26, 2Q26), *willingness to pay* (1Q23, 2Q23 only), *host pricing tools* (2Q23 only, as a **moderating** force), *FX* (EMEA/LatAm/APAC primary driver 4Q24–1Q26).
4. **The mix content, in management's words:** short-term stays and entire homes outpacing long-term stays and private rooms; **4+ bedroom listings growing fastest** (4Q25, 1Q26, 2Q26); groups of 5+ the fastest-growing NA segment (1Q24, 2Q24); **Bedroom Nights Booked +12% vs nights +10% in 2Q26**; average nights per booking 3.7 (FY25) vs 3.8 (FY24), by region 4.1 / 3.8 / 3.6 / 3.3.
5. **The event dates,** all filed: cancellation redesign October 2025 (global); single-fee tranche 1 October 2025 + the December non-PMS step; RNPL US August 2025; RNPL global 17 February 2026; tranche 2 announced July 2026 to complete in 2026; cross-currency fee from Q2 2024 on ~20% of GBV; total price display global default April 2025.
6. **"The increase in ADR was driven in part by the continued adoption of RNPL"** — 2Q26 10-Q, the only *filed* RNPL→ADR causal sentence.
7. **"We saw a 3% increase in ADR in 2025… primarily due to higher ADR in EMEA, which increased by 8%"** — FY2025 10-K.
8. **GBV definition:** *"GBV represents the dollar value of bookings on our platform in a period and is **inclusive of host earnings, service fees, cleaning fees, and taxes, net of cancellations and alterations** that occurred during that period"* (10-K, 10-Q, and every letter's Key Business Metrics box). This is what licenses treating cleaning-fee removal and the cross-currency fee as ADR terms at all.
9. **ADR definition:** the letters' KPI table line is literally *"Gross Booking Value per Night and Seats Booked (or ADR)"* — i.e. **the seats denominator is in the metric**, from 2Q25 onward.
10. **The 3Q26 guide's omission of FX from the ADR sentence** (2Q26 letter) — a filed, dated, qualitative statement.

### 4.2 TRANSCRIPT MIRROR — usable, but must be labelled on the slide

1. **The two bundle magnitudes: 4Q25 ">200bp nights / ~300bp GBV" (D014) and 1Q26 "~3 points nights / ~4 points GBV" (D032).** These are the only numbers that imply **~1pp of ADR from the bundle in each of 4Q25 and 1Q26**. They are **not in any SEC filing** (X3 §3–§4, checked: both 8-K Ex-99.1s, FY25 10-K, 2Q26 10-Q; 1Q26 10-Q open). `nights_v2_design.md` §3.1: *"the dates are SEC-filed and the magnitudes are not."* `D2_d2_nights_4q26_lap.md` §7 Conflict 6: *"The dates are solid; the magnitude is not, and the memo should not present them as equally sourced."*
2. **2Q26 gave no figure (D045).** First print since 3Q25 with no quantified bundle contribution. A 3Q26 restatement (or not) is the single disclosure that decides the lap case — adrv3 N memo 2 thresholds: ≤1.5 points → case B, ≥2.5 → case A.
3. **D016 (4Q25): RNPL → "mix shift towards larger entire homes, especially those with four or more bedrooms, contributing to the increase in ADR."** Direction disclosed; ratio never.
4. **Single-fee supply coverage: "over a quarter of our active listings" (D041, 1Q26 call) and "approximately half" (D047, 2Q26 call).** ⚠ **`data/processed/overnight/06_fee_timeline.csv` rows 16 and 19 attribute these to the 1Q26 and 2Q26 letters. That is a misattribution** — D041/D047 record them as call-only, and my own read of both letters' fee paragraphs confirms neither carries a percentage. Fix or footnote before use.
5. **D053 (2Q26 call, Chesky): AI pricing is "many multiples bigger than RNPL."** Management's own relative sizing; no number.

### 4.3 TEAM INFERENCE — never attribute to management

- **The ~1pp ADR contribution itself** is our arithmetic (GBV points minus nights points) on D014/D032. Management gave the two legs, not the difference.
- **Fee-reprice mechanics:** a payout-neutral host reprice moves the migrated cohort's ADR by **0.5–0.8%**; migrated-cohort y/y share 12–22pp in 4Q25–2Q26 ⇒ **0.09–0.15pp of the residual** (K2, descriptive). The imposed coefficient is 0.007 pp per pp of share (range 0.000–0.038); the *fitted* coefficient is 0.114, **16× the mechanics**, and `docs/adrv3/SYNTHESIS.md` §5 says flatly **"do not use K's fitted coefficient anywhere."**
- **Tranche-2 deadline dates** (15 Sep non-EEA, 13 Oct EEA/CH) come from a vendor notice, not a filing.
- **Seats/new-business ADR dilution** (−0.48pp assumed in 3Q26) — never disclosed.
- **Cross-currency fee → ADR:** the mechanical link (service fee inside GBV) is ours; management discusses the fee only in take-rate/revenue terms.
- **The like-for-like pricing residual (+4.85pp carried in 3Q26) is unobserved and its rule is post-hoc** (`last_q`, promoted 11 Sep after seeing J3's table). `docs/adrv3/SYNTHESIS.md` §3: management's ~1pp bundle attribution "is half of each quarter's step over the 2023-25 mean… **the other half of the step, and all of 2Q26's, is unexplained.**"
- **NA ex-FX ADR from 2Q25 onward** (3.33 / 5.05 / 4.78 / 6.30 / 6.75) is a reconstruction, not a disclosure.

### 4.4 Kill list — `docs/revenue-forecast-strategy/AGENT_BRIEF.md` §6, "never quote these as ours"

ADR-relevant entries, verbatim:
- **"half of ADR growth is bigger units" (it is +0.46–0.8pp)** ← the party-size term. D4's card value is **+0.797pp**, "a fifth of the ex-FX move, never half."
- **"+4.05% fee uplift" as measured.**
- **the −3.4pp Q4 FX step (double subtraction).**
- **"82% of Q4 FX already determined."**
- Also on the list and adjacent: *"the 1.71M quote panel as 'fee-inclusive' (it is not)"*, *"restated unearned fees (`reported / (1 − d)`) as a pin or a feature (circular)"*, *"the 120-market panel as a nights measurement"*. Full lists: `docs/revenue-forecast-strategy/05_backtests/RED_TEAM.md`, `research/notes/overnight/14_master-synthesis.md` §11.
- From `docs/adrv3/SYNTHESIS.md` §5, same force: **do not use K's fitted coefficient; do not use L's primary model's numbers (+0.6 / +1.1 ex-FX) for anything.**

### 4.5 Contradictions and gaps found while building this

1. **Fee-tranche start date.** D013 note: the 3Q25 letter says **"In October"**; the 2Q26 call says **"September of last year"**; the 1Q26 letter says **"Beginning in Q4 2025."** → the start is a **September–October 2025 range, not a point.**
2. **One tranche or two inside 4Q25.** D024 note: "**Two dated tranches inside 4Q25, not one. PR #32 models a single October tranche.**" (PMS hosts from October; most non-PMS single-fee hosts to 15.5% from December.)
3. **`06_fee_timeline.csv` misattributes the "over a quarter" / "about half" single-fee coverage to the letters** (rows 16, 19). They are call-only. See §4.2 item 4.
4. **2Q26 APAC ex-FX ADR:** `04_regional_quarterly_wide.csv` row 23 = −1.3509 (basis "disclosed-chained") vs `10_regional_panel_quarterly.csv` row 24 = **blank**. The letter gives no figure. **Blank is correct.**
5. **2Q25 letter text missing from the local cache** — the global ADR driver clause for 2Q25 is not reproduced here.
6. **`data/raw/letters/` does not exist in this checkout**; every `source_file` path in `02_guidance_ledger.csv` and `02_kpi_panel_long.csv` points at files that are gitignored. Quotes are re-verified here against the OneDrive PDF-text cache, which is a **different extraction of the same documents**, not the filed HTML.
7. **1Q26 10-Q (accession 0001559720-26-000014) has never been read.** It is the only filing that could still carry a filed bundle magnitude (X3 §8). One fetch closes it.

---

## 5. What the mechanism build gets, in one place

**Filed skeleton (regional underlying + bundle + events, each with a filed anniversary):**

| leg | filed evidence | anniversary |
|---|---|---|
| EMEA price appreciation | ex-FX +3 to +5pp every quarter 2Q25–2Q26; FY25 10-K "EMEA ADR +8%" | none (level) |
| LatAm / APAC price appreciation | ex-FX +2 to +3pp, stable, FX-dominated reported | none |
| NA mix (entire homes, 4+ bedrooms, ST over LT) | NA reported +5/+5/+7/+7 in 3Q25–2Q26; "extending a mix-shift trend we have now seen for over a year" (2Q26) | trend, not an event |
| Bedroom-nights size term | 2Q26: **+12% vs nights +10% ⇒ ~2pp**, filed | new metric; one observation |
| RNPL, US | D008 filed (Aug 2025) | **3Q26** |
| RNPL, ex-NA | D025 filed (17 Feb 2026) | **1Q27** |
| Cancellation redesign, global | D060 filed (Oct 2025) | **4Q26** |
| Single fee tranche 1 | D024 filed (27 Oct 2025 + Dec step) | **4Q26** |
| Single fee tranche 2 | 2Q26 letter (July 2026 announcement, complete in 2026) | **peaks 4Q26, laps 4Q27** |
| Cross-currency fee | 4Q24/1Q25 letters (from Q2 2024, ~20% of GBV) | **2Q25 (already lapped)** |
| Seats dilution | Services/Experiences from May 2025; supply +80% y/y in 2Q26 | **2Q26 onward, never sized** |
| FX | disclosed 17-quarter ADR-FX series; gross of hedging | contemporaneous, no lap |

**The bundle's ADR contribution (~1pp in 4Q25 and ~1pp in 1Q26) is the only place where the mechanism can be pinned to management's own arithmetic — and it is transcript-only. Say so on the slide, put the filed "roughly 20% of global GBV" beside it, and flag that 2Q26 carried no figure at all.**
