# ADR line, mitigation D: the origin proxy at QUARTERLY frequency, and its first price link

**The raw review text IS on this machine.** `~/abnb_ia_capture/<country>/<state>/<market>/<dump>/reviews.csv.gz`,
**120 markets, 7.4 GB gzipped, 65.9m review rows**, each with `listing_id`, `date` and `comments`. Branch 2 of
the task (falling back to dump vintages of the annual shards) was therefore **not** taken. What is *not* on the
machine is more than one review vintage per market: 119 of the 120 files are June 2026 dumps and one (Vaud) is
2026-08-10, so the panel below is a **single-vintage** read and the caveat in §5 is load-bearing.

Date: 22 September 2026. Branch `theo/pitch-model-v2`.
Code `analysis/src/pitch_model_v2/adr_engine/origin_language.py`.
Outputs `data/processed/pitch_model_v2/adr_engine/origin_lang_*.csv`.

```
cd ~/Citadel-ABNB && PYTHONPATH=analysis/src python3 -W ignore -m pitch_model_v2.adr_engine.origin_language
# first run: --workers 8, ~30 min over the 7.4 GB corpus; exit 0
# re-runs read origin_lang_cache_counts.csv / origin_lang_cache_price.csv and finish in <1 s; --rebuild forces the raw pass
```

## 0. What this is, in one paragraph

`adr_v2_geomix_prereg.md` §4 carries an origin proxy built from reviewer language and states two weaknesses:
it is **annual**, so the origin story has no time dimension, and it has **no price**. Both are fixed here, off
the raw corpus rather than the pre-aggregated shards. The language classifier is
`abnb_party_size_reviews_v2.lang_of` **imported verbatim** — same eight buckets, same stopword signatures, same
tie rules — so the quarterly object is the annual object at higher frequency and nothing about the measurement
changed. (A vectorised replication was checked against `lang_of` on 200,000 Athens reviews: agreement
**1.00000**; the loop form is what actually runs.) The new facts are: (a) English loses **2.7–3.2pp of review
share every quarter, four quarters running**, a steadiness the annual series could not show; (b) because a
review carries `listing_id`, the reviewed listing's nightly price joins on, and **within the same market the
listing reviewed in a non-English language is consistently cheaper than the one reviewed in English** (median
0.85–0.89 of the English listing, in 93% of 688 market-language cells); (c) pricing the rotation on those fixed
within-market levels, the language mix alone takes **−0.69% off the price of the listing reviewed, globally,
2024→2026** (LatAm −1.12, EMEA −0.89, APAC −0.38, NAM −0.13; 109 of 120 markets negative). That is the first
time this object has produced a price at all. It stays **descriptive** and does not enter the ADR term — §5
says why.

## 1. What ran, and the coverage

| | |
|---|---|
| Raw files | 120 `reviews.csv.gz`, one dump per market, 7.4 GB gz |
| Dump dates | 2026-06-14 … 2026-06-30 (119 markets) + `switzerland_vd_vaud` 2026-08-10 |
| Raw rows read | **65,941,392** |
| Rows classified (date ≥ 2021-01-01, ≤ dump) | **53,253,328** |
| Panel | market × quarter × language, **2021Q1–2026Q2**, 8 buckets |
| Markets mapped to a reporting region | **120 / 120**, 0 UNMAPPED |

Region mapping is `market_currency_map.csv`. One defect was found and fixed: the capture store spells Tokyo
`japan_kantō_tokyo` and the engine's map spells it `japan_kanto_tokyo`, so a naive join dropped **the only
Japanese market in the panel** out of APAC. `origin_language._nk()` strips combining marks before joining.
Markets in the map with no review dump on disk: `malta`, `new-zealand` (and the country-level rows `ireland`,
`japan_kanto_tokyo`, whose market-level equivalents are present).

| region | markets | reviews 2021Q1–2026Q2 |
|---|---:|---:|
| EMEA | 55 | 27,441,278 |
| NAM | 42 | 13,235,597 |
| LatAm | 7 | 6,365,590 |
| APAC | 16 | 6,210,863 |
| **total** | **120** | **53,253,328** |

**Final quarter is truncated.** The June dumps observe a median **96.7%** of 2Q26's days (range 82.4–100%),
so 2Q26 *levels* are short by a few percent and 2Q26 y/y level growth is depressed mechanically (English
+2.9% in 2Q26 against +24.4% in 1Q26 — that is the calendar, not the guest). Every growth statement in this
note is therefore made either on **shares** or on **day-matched LTM windows** ending at each market's own dump
date (`ltm0` = the 365 days to the dump, `ltm1` = the 365 before that, `ltm2` = the 365 before that), never on
raw quarterly levels.

## 2. The quarterly panel (`origin_lang_global_quarter.csv`, `origin_lang_region_quarter.csv`)

GLOBAL share of reviews, %. n per quarter runs 1.14m (2022Q1) to 4.20m (2025Q3); 4.11m in 2026Q2.

| quarter | en | es | other | de | fr | pt | zh_ja_ko | it |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2022Q1 | 70.5 | 11.4 | 7.5 | 1.8 | 4.5 | 2.2 | 1.1 | 1.1 |
| 2023Q2 | 66.3 | 13.3 | 7.1 | 3.9 | 4.6 | 2.0 | 1.9 | 1.0 |
| 2024Q2 | 63.1 | 14.2 | 8.2 | 4.1 | 4.8 | 2.4 | 2.2 | 1.0 |
| 2025Q2 | 59.3 | 16.2 | 9.1 | 4.4 | 4.6 | 3.0 | 2.2 | 1.1 |
| 2025Q4 | 56.8 | 17.4 | 10.2 | 3.7 | 4.1 | 3.8 | 2.8 | 1.1 |
| 2026Q1 | 55.8 | 17.8 | 10.5 | 3.2 | 4.0 | 4.2 | 3.2 | 1.2 |
| **2026Q2** | **56.3** | **17.4** | **10.1** | 4.7 | 4.6 | 3.5 | 2.3 | 1.1 |

The annual object said English 71% (2022) → 58% (2026); the quarterly object reproduces that and adds the
**shape**, which is what the line needed. Language shares are strongly **seasonal** (English peaks in Q2, es/pt
peak in Q1 — southern-hemisphere and Latin holiday timing), so shares must be read y/y, not q/q. Read y/y the
series is close to a straight line:

| English share, y/y change (pp) | 2025Q3 | 2025Q4 | 2026Q1 | 2026Q2 |
|---|---:|---:|---:|---:|
| GLOBAL | −2.79 | −3.21 | −2.73 | −2.91 |
| EMEA | −2.62 | −2.72 | −2.26 | −3.04 |
| LatAm | −1.94 | −2.74 | −3.54 | −2.39 |
| APAC | −0.71 | −1.82 | −1.45 | −2.28 |
| NAM | −0.68 | −0.65 | −0.93 | −0.32 |

English share by region, 2026Q2: NAM 89.7, APAC 77.9, **EMEA 49.7**, LatAm 12.2. Q2 is EMEA's English-peak
quarter, and the Q2 series runs **64.9 → 58.8 → 55.9 → 52.7 → 49.7**: 2Q26 is the first Q2 below 50.
**No sign of deceleration in the rotation** through the last observed quarter — the four-quarter run is flat at
about −2.9pp a year globally, and APAC is the one region where it is *accelerating* (−0.7 → −2.3pp).

## 3. (a) The rotation, day-matched (`origin_lang_rotation_ltm.csv`)

LTM to each market's dump (≈ Jul 2025–Jun 2026) vs the same 365 days two years earlier. **Levels carry
attrition (§5); the column to read is the share and the growth *relative to the panel's own total*.**

GLOBAL, n = 10.19m / 12.73m / 15.82m reviews across the three windows:

| lang | share 2024 | share 2025 | share 2026 | growth 24→26 | growth 25→26 | **excess over panel total, 25→26** |
|---|---:|---:|---:|---:|---:|---:|
| en | 62.94 | 59.60 | **56.76** | +40.0% | +18.3% | **−5.9pp** |
| es | 14.80 | 16.13 | **17.45** | +82.9% | +34.3% | **+10.1pp** |
| other | 8.05 | 9.04 | **10.05** | +93.6% | +38.1% | **+13.8pp** |
| de | 3.70 | 3.91 | 4.01 | +68.0% | +27.3% | +3.1pp |
| fr | 4.50 | 4.50 | 4.32 | +49.1% | +19.4% | −4.9pp |
| pt | 2.50 | 3.07 | **3.61** | **+124.1%** | **+45.8%** | **+21.6pp** |
| zh_ja_ko | 2.40 | 2.56 | 2.66 | +71.9% | +28.7% | +4.4pp |
| it | 1.11 | 1.18 | 1.15 | +60.8% | +20.8% | −3.4pp |
| **ALL_NON_EN** | **37.06** | **40.40** | **43.24** | **+81.0%** | **+32.9%** | **+8.7pp** |
| TOTAL | 100 | 100 | 100 | +55.2% | +24.2% | — |

Non-English reviews grew **twice as fast as English** over two years (+81% vs +40%) and non-English share went
**37.1 → 43.2%**. The drivers, in order: **Portuguese (+124%), "other" (+94%), Spanish (+83%)**; German and
East-Asian are mid-pack; French and Italian are *losing* share. By destination region:

| region | en 24→26 | non-en 24→26 | non-en share 2024 → 2026 |
|---|---:|---:|---|
| LatAm | +56.3% | **+129.6%** | 80.3 → **85.7%** |
| APAC | +58.8% | +95.6% | 18.6 → 21.9% |
| NAM | +41.6% | +65.8% | 9.5 → 10.9% |
| EMEA | +31.5% | +63.6% | 44.9 → **50.3%** |

EMEA crossed over: **more than half the reviews written in EMEA destinations in the last twelve months were
not in English.** Within EMEA the movers are "other" (+86.8%, 10.0 → 12.8% share) and Portuguese (+101%);
within APAC it is Spanish (+183%, off a small base) and "other" (+94%); within LatAm everything ex-English.

## 4. (b) Against the filed origin statements (`origin_lang_filings_crosscheck.csv`)

The panel's own LTM total grew +24.2% (attrition, §5), so a language's growth is only interpretable **net of
its scope**. `excess_pp` below is the language's LTM growth minus the growth of the scope it sits in. For
reference, disclosed company nights grew **+9.5% LTM to 2Q26** (560.0m vs 511.3m, `02_kpi_panel_quarterly`).

| check | n mkts | n reviews LTM26 | share of scope 24 → 26 | growth 25→26 | **excess vs scope** | filed statement |
|---|---:|---:|---|---:|---:|---|
| **pt outside Brazil/Portugal** | 113 | 96,012 | 0.60 → 0.68% | +35.4% | **+11.9pp** | Brazil origin +21/+21/+31 y/y, ≈ **+23.5% LTM** = **+14pp** over company nights |
| pt inside Brazil/Portugal (control) | 4 | 474,279 | 22.2 → 29.3% | +48.1% | +16.9pp | domestic Portuguese |
| **es outside Spanish-speaking dest.** | 107 | 1,503,331 | 9.86 → 11.34% | +30.1% | **+6.9pp** | LatAm ≈20% of nights, LatAm nights +18–22% y/y |
| es inside Spanish-speaking dest. (control) | 13 | 1,256,149 | 42.7 → 49.1% | +39.7% | +10.2pp | intra-Hispanophone |
| **zh_ja_ko outside APAC** | 104 | 201,235 | 1.32 → 1.45% | +30.1% | **+6.4pp** | China outbound; Japan origin "high-teens" 2Q26 |
| zh_ja_ko inside APAC (control) | 16 | 218,959 | 10.70 → 11.24% | +27.3% | **−0.1pp** | intra-APAC |
| en, whole panel | 120 | 8,978,323 | 62.9 → 56.8% | +18.3% | **−5.9pp** | — |

Reading these honestly:

- **Brazil corroborates, and the magnitude lines up.** Cross-border Portuguese runs **+11.9pp above its scope**;
  the filed Brazil-origin statement runs **+14pp above company nights**. Two independent measurements of the
  same phenomenon, one of them Airbnb's own guests, landing within ~2pp. This is the cleanest cross-check in
  the note. Caveat: Portuguese outside Brazil/Portugal is also Portuguese, Angolan and Mozambican guests, and
  it is a **small** absolute object (96k reviews LTM, 0.68% of the non-Lusophone panel).
- **LatAm corroborates directionally**, +6.9pp of excess on cross-border Spanish, against a disclosed LatAm
  nights rate roughly 9–11pp above company. Weaker than Brazil, and note the intra-Hispanophone control grows
  *faster* (+10.2pp excess): a good part of the Spanish story in this panel is **intra-regional**, not
  long-haul, which is exactly the flavour the four-region term struggles with.
- **East Asia splits the two cells, informatively.** East-Asian-language reviews grow **+6.4pp above scope
  outside APAC** and **−0.1pp inside APAC**. Whatever East-Asian outbound is doing, in this panel it is landing
  in EMEA and the Americas, not in intra-APAC destinations. That is consistent with `od_layer`'s measured cell
  (China→Japan arrivals −58.2% y/y) and cuts against reading "APAC nights +18%" as an intra-APAC story.
- **India is invisible and stays invisible.** Indian guests write English. India-origin nights are filed at
  +50/+50/+60% and the English bucket in this panel is *shrinking* 5.9pp faster than the scope. **The single
  largest disclosed origin story cannot be seen in this object at all**, and any claim that the review-language
  panel "confirms the origin mix" must be stated with that hole named.

## 5. (c) The price link — what is possible, and what it says

**Do price and review language ever co-occur in one file?** Not in one file, but in one **join**: a review
carries `listing_id`, and `listings.csv.gz` from the same dump carries that listing's nightly `price`,
`accommodates` and `room_type`. So for every market we can ask: *of the listings reviewed in the last twelve
months, how does the one reviewed in language L price against the one reviewed in English?* That is computed
for **all 120 markets** (not 5–10), in `origin_lang_price_by_lang.csv`, restricted to cells with ≥20 reviews
(892 cells, median cell **2,407** reviews).

**Pooled result** (cells with ≥100 reviews, and the market's English cell ≥100; ratio to the same market's
English median, so no currency conversion and no cross-market comparison enters):

| lang | markets | median price ÷ English | markets cheaper than English | median price-per-person ÷ English | LTM26 reviews |
|---|---:|---:|---:|---:|---:|
| es | 113 | **0.848** | 109 / 113 | 0.881 | 2,759,244 |
| pt | 71 | **0.856** | 68 / 71 | 0.881 | 568,890 |
| it | 72 | 0.860 | 69 / 72 | 0.875 | 179,688 |
| fr | 102 | 0.865 | 92 / 102 | 0.915 | 682,576 |
| de | 107 | 0.879 | 96 / 107 | 0.973 | 633,850 |
| other | 119 | 0.889 | 114 / 119 | 0.928 | 1,589,641 |
| zh_ja_ko | 104 | 0.889 | 92 / 104 | 0.906 | 419,461 |

Across all 688 non-English cells with n ≥ 100, the median ratio is **0.870** and **93.0%** are below 1; across
the 12 largest markets, 83 of 84 cells (median 0.833). Examples: Mexico City es 0.636, Rio pt 0.671, London
zh_ja_ko 0.735, Paris fr 0.718, Rome it 0.743, Tokyo zh_ja_ko 0.928, Los Angeles es 0.878.

**Pricing the rotation** (`origin_lang_price_mix_effect.csv`, `origin_lang_price_mix_market.csv`): hold each
language's median nightly price **fixed at its LTM-2026 level inside each market** and move only the language
shares from the LTM-2024 window to the LTM-2026 window. Everything is within market, so market mix, currency
and the general level of prices all net out; what is left is the composition effect of the rotation.

| region | markets | mix effect 24→26 | mix effect 25→26 | same, per person | markets negative |
|---|---:|---:|---:|---:|---:|
| LatAm | 7 | **−1.12%** | −0.63% | −1.09% | 7 / 7 |
| EMEA | 55 | **−0.89%** | −0.44% | −0.68% | 50 / 55 |
| APAC | 16 | −0.38% | −0.19% | +0.00% | 15 / 16 |
| NAM | 42 | −0.13% | −0.06% | −0.12% | 37 / 42 |
| **GLOBAL** | **120** | **−0.69%** | **−0.35%** | **−0.53%** | **109 / 120** |

Largest negatives: Mexico City −2.31%, Istanbul −2.23%, Bogotá −2.21%, Bordeaux −2.02%, Paris −1.88%,
Santiago −1.73%, Venice −1.72%, Rome −1.66%. The only material positive is Hong Kong (+0.92%).

**This is the right order of magnitude to matter and the wrong object to put in the term.** −0.35% a year on
the price of the listing reviewed sits inside the same band as the ADR line's own sub-regional country-mix term
(mean −0.45pp over 2023–26, `geomix_subregional_term.csv`), and it is a **different channel**: the country-mix
term moves nights between markets, this moves guests between price points *inside* a market, which is precisely
the cell `adr_v2_geomix_prereg.md` §4 calls "outside this object entirely". Two independent composition drags
of similar size, not one counted twice.

## 6. Honest limits

1. **Single vintage.** One review dump per market, so every quarter is read off the listings live in June 2026.
   Delisted listings take their whole review history with them. The panel's LTM total grows **+24.2%** against
   company nights **+9.5%** — roughly **15pp of pure attrition inflation** — and it is *not* uniform (NAM **+15.0**,
   EMEA **+13.3**, APAC **+11.0**, LatAm **+24.2pp** over the disclosed regional nights rates for the same
   four quarters, 6.5 / 6.5 / 16.5 / 19.5%). **No level or level-growth in this
   note is a nights number.** Shares within a quarter, y/y share changes, and growth stated net of scope are
   the statistics that survive; that is why §3 and §4 are written in those terms.
2. **Language is not origin.** It is the language the guest chose to write in. Spanish in Madrid is mostly
   Spaniards; the cross-border scopes in §4 are the attempt to net that out, and they are crude (Switzerland
   counts as a German, French *and* Italian destination, so it is excluded from none of them).
3. **India is unobservable.** Indian guests write English, so the largest filed origin story (+50/+50/+60%) is
   inside a bucket that is *falling*. The panel also has **no Indian destination market**, so neither side of
   the India story is visible. Anything the line says about India is not supported by this object.
4. **The price is a snapshot, not a transaction.** `price` is the listing's advertised nightly rate at the June
   2026 dump, joined to reviews written up to a year earlier. It is a within-market cross-section of **price
   levels of the listings guests of each language stay in** — it is not an ADR, not a paid rate, and not
   FX-translated (all ratios are against the same market's English cell, in local currency).
5. **The cheaper-listing result is partly a room-type result.** The entire-home share of the listing reviewed
   is also lower for every non-English bucket (median ratio to English: zh_ja_ko 0.84, other 0.93, es 0.93,
   de 0.95, it 0.97, pt 0.97, fr 0.98). Normalising by `accommodates` keeps about three-quarters of the effect
   (per-person mix effect −0.53% vs −0.69% globally), so it is not *only* room type, but it is not a clean
   like-for-like either. Not stated as a price elasticity, and not stated as a demand-side preference.
6. **Reviews are not nights.** Review propensity differs by language, by stay length and by listing turnover,
   and the composition of that propensity may itself be drifting. The level of any language share is therefore
   not the level of that origin's nights share; only the **direction and the pace** are being claimed.
7. **`other` is 10% of the panel and rising fastest after Portuguese**, and the classifier cannot say what it
   is. Dutch, Polish, Turkish, Hebrew, Arabic, Scandinavian and Russian all land there. The largest single
   contributor to the EMEA rotation is a bucket we cannot name.

## 7. Verdict

**The origin proxy now has a time dimension and a price, and both point the same way as the thesis.** The
quarterly panel shows English losing 2.7–3.2pp of review share in each of the last four quarters with no
deceleration, EMEA crossing below 50% English, and non-English reviews growing twice as fast as English over
two years. The filed Brazil-origin statement is corroborated to within ~2pp by cross-border Portuguese on
Airbnb's own guests; LatAm is corroborated directionally but turns out to be substantially intra-regional;
East-Asian outbound shows up outside APAC and not inside it; India is invisible and must be said to be.
The price link, which the pre-registration said did not exist, does exist descriptively through `listing_id`:
non-English guests stay in cheaper listings in 93% of 688 market-language cells, and the rotation alone takes
**−0.69% off the within-market price of the listing reviewed over two years, −0.35% in the last year**.
**It should stay an exhibit.** It is a single vintage, reviews are not nights, the price is a snapshot and not
a rate paid, and India — the biggest disclosed origin number — is structurally invisible. It corroborates the
direction of the four-region tilt and the `od_layer` finding that the named origins' growth is ex-NA; it is
not a forecast input and nothing in the ADR term should be re-fitted on it.

## RESUME

`origin_language.py` reads the **raw** Inside Airbnb review corpus — which **is** on this machine, 120 markets,
7.4 GB gz, **65.9m rows, 53.3m classified** — and rebuilds the repo's annual reviewer-language origin proxy at
**quarterly** frequency 2021Q1–2026Q2, using `abnb_party_size_reviews_v2.lang_of` imported verbatim (a
vectorised replication agreed with it 1.00000 on 200k reviews). Only **one review vintage exists per market**
(119 June-2026 dumps + Vaud 2026-08-10), so levels carry delisting attrition — the panel's LTM total grows
+24.2% against company nights +9.5% — and every claim is made on shares, on y/y share changes, or on growth net
of scope, never on levels. Quarterly, **English review share falls 2.79 / 3.21 / 2.73 / 2.91pp y/y in the last
four quarters with no deceleration**, EMEA prints another **sub-50% English quarter (49.7% in 2Q26; the first was 4Q25 at 49.5%, corrected 23 Sep)**, and on
day-matched LTM windows non-English reviews grew **+81.0% vs English +40.0%** 2024→2026 (non-English share
37.1 → 43.2%), led by **Portuguese +124%, "other" +94%, Spanish +83%**; French and Italian are losing share.
Against the filings: cross-border Portuguese runs **+11.9pp above its scope** where the filed Brazil-origin
statement runs +14pp above company nights (**the two measurements agree to ~2pp**); cross-border Spanish +6.9pp
but with a *faster* intra-Hispanophone control, so LatAm is substantially **intra-regional**; East-Asian
languages **+6.4pp outside APAC and −0.1pp inside it**, consistent with `od_layer`'s China→Japan −58.2%; and
**India is invisible** — Indian guests write English, the English bucket is shrinking, and the panel has no
Indian destination market either. The pre-registration's "what it does not give is a price" is now **false**:
reviews carry `listing_id`, so the reviewed listing's nightly price joins on, and within the same market the
non-English-reviewed listing is cheaper in **93.0% of 688 cells (median ratio 0.870)**; holding those levels
fixed and moving only the language shares, the rotation takes **−0.69% off the within-market price of the
listing reviewed 2024→2026 (−0.35% last year; LatAm −1.12, EMEA −0.89, APAC −0.38, NAM −0.13; 109 of 120
markets negative)** — the same order as the line's sub-regional term (−0.45pp) but a **different channel**
(guests moving between price points inside a market, not nights moving between markets). Also fixed on the way
through: the capture store spells Tokyo `japan_kantō_tokyo` and `market_currency_map.csv` spells it
`japan_kanto_tokyo`, so a naive join silently dropped the panel's only Japanese market out of APAC. **Verdict:
exhibit, not input** — single vintage, reviews are not nights, the price is a June-2026 snapshot and not a rate
paid, room type explains about a quarter of the price gap, and the largest disclosed origin story cannot be
seen. Next, if the line wants this promoted: a **second review vintage** for even 20 markets would kill the
attrition caveat outright and turn the level growth into something readable.
