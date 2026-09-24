# World Cup premium inside the 2Q26 ADR core — pre-registration

**22 September 2026**, written before any price or availability outcome was computed by treatment. Branch
`krish/worldcup-premium`, package `analysis/src/worldcup_premium/`, outputs `data/processed/worldcup_premium/`.
Motivation: `docs/pitch-model-v2/dossiers/ADR_AUDIT_krish.md` (branch `theo/pitch-model-v2`) finding F5. The ADR
line carries the 2Q26 core flat through 2027. ADR is booking-dated, and the nights line says World Cup nights were
booked mostly in 2Q26. Any event premium in 2Q26 bookings therefore sits inside the carried core, and it does not
recur in 4Q26. The audit's break-even: the 2Q26 core must hold 0.44–1.02pp of non-recurring event premium for 4Q26
ADR to reach the Street's $171.33. This file fixes how that premium is measured.

**What was looked at before writing this** is mechanics only, with no price or availability compared across
treatment groups:

- Quote coverage, lead time and stay length per dump.
- Which calendar snapshots exist and whether they carry prices.
- The count of Common Crawl search pages.
- The match schedule.

**Provenance, stated against ourselves.** This file is not committed before the results; commits are the humans'
call. Its blob hash is logged by `run.py` at every run. The ordering is attested only by this session, the same
limitation the audit flagged for `adr_fx_prereg.md`. Every number below reproduces deterministically from the
on-disk dumps.

## 1. Sources

| source | use | status |
|---|---|---|
| Inside Airbnb monthly listings, 2026 (`data/raw/inside_airbnb/*_2026-*_listings.parquet`) | P1 quotes panel | on disk, sanctioned |
| Inside Airbnb June/July 2026 single snapshots (`data/raw/inside_airbnb_reviews/*_2026-*_listings.csv.gz`) | P2 quotes cross-section | on disk, sanctioned |
| Inside Airbnb calendars (`data/raw/inside_airbnb_calendar/`) | V1–V3 per-date availability; A1 Paris 2024 prices | on disk, sanctioned. Priced through May 2025; availability-only after. |
| Reviews stays panel (`data/processed/q3nowcast/E/market_monthly_yoy.csv`) | V4 realised stays | on disk |
| Match schedule: 104 matches, date × stadium (`data/processed/worldcup_premium/wc2026_matches_by_venue.csv`) | event nights | parsed from Wikipedia raw wikitext (12 group pages, round of 32, knockout, final), 22 Sep 2026 |
| Common Crawl search pages | none | **Unusable.** 1–30 host-city search pages per 2025–26 crawl; post-2024 pages carry no quotes (memory `cc-search-price-panel`); 72 Paris pages in all 2024 crawls, none dated in the Olympic window. Recorded, not used. |

No scraping, and nothing touching airbnb.com.

## 2. Geography (mechanical)

Venue coordinates are frozen in `config.VENUES`. Each market's centroid is the mean latitude/longitude of its
2026 listings.

- **Host:** the centroid is within 75 km of a venue. Its schedule is that of the nearest venue.
- **Ring:** 75–200 km from a venue. Reported, never used as control.
- **Control:** more than 200 km from every venue, North America only.

Two exclusions and one placebo:

- New York City is excluded from price. Local Law 18 makes 76–78% of its quotes 30-night stays; MetLife is
  represented by Newark and Jersey City.
- The Dallas snapshot (scraped 20 July, after the tournament) is excluded from price and used as a placebo.

## 3. Nights

- **T (tournament):** nights 11 June – 19 July 2026 inclusive.
- **Match nights M_v:** for each match at venue v on date d, the nights of d−1 and d.
- **A (adjacent, no event):** nights 14 May – 7 June and 24 July – 16 August 2026.
- **Weekend night:** the nights of Friday and Saturday.

Controls get **pseudo** match nights from their nearest venue's schedule, as a placebo.

## 4. Price

Asking prices only. The quote is `price_quote_price_per_night` on the quoted stay [check-in, check-out). It is
pre-fee, from the 2026 basis, and is never compared with pre-2026 prices.

**Common sample:** stays of 1–7 nights; check-in 0–45 days after the scrape; $10 ≤ price per night ≤ $5,000;
check-in on or after the scrape date.

**P1 — primary.** Same-listing panel in the two hosts with monthly dumps (Los Angeles, Mexico City) against the
controls with monthly dumps (Chicago, Austin, Nashville, New Orleans), dumps March–August 2026.

`log ppn = listing FE + stay-length FE + lead-bin FE (0–3, 4–7, 8–14, 15–30, 31–45) + check-in-week FE + b_wkd·weekend_share + b_T·(host × T_share) + b_M·(host × M_share) + c_T·T_share + c_M·pseudoM_share`

- **Estimand:** the event-window premium π̄ = exp(b_T + b_M · m̄) − 1, where m̄ is the mean share of T nights
  that are match nights at the market's venue.
- **Inference:**
  - listing-clustered 90% interval;
  - leave-one-control-out range;
  - rank of the observed (b_T + b_M·m̄) among all 15 two-market "treated" pairs drawn from the six markets.
  With two treated markets, no market-level p-value is claimed.

**P2 — secondary.** Within-snapshot match-night premium, all host snapshots with in-T quotes, against control
snapshots scraped 14–30 June 2026. Sample: check-in ≤ 19 July.

`log ppn = market FE + stay-length FE + lead-bin FE + room type + accommodates (capped at 16) + bedrooms (capped at 6) + neighbourhood FE + b_wkd·weekend_share + g·M_share + h·(host × M_share)`

- **Estimand:** the match-night premium in hosts net of the pseudo-match placebo, (g + h) − g.
- **Reported separately:** the placebo coefficient g in controls, and the Dallas post-tournament placebo.
- **Inference:** market-clustered 90% interval, plus leave-one-host-out.

**P3 — robustness.** P1 without check-in-week FE but with market × check-in-month FE for controls only, reported
beside P1.

## 5. Volume and booking timing (calendar availability)

U(m, s, d) is the share of active listings in market m, snapshot s, that are unavailable (`available = f`) on
date d. **Active** means at least one available day in the snapshot's 365-day horizon and less than 95% of days
blocked. "Unavailable" is booked **or** host-blocked; the two cannot be separated.

- **V1 — excess booked share (primary volume).** At each snapshot round, X(m, s) = mean U over T nights on or
  after s + 1 minus mean U over A nights. The estimand is X(host) − mean X(controls) in the same round.
  - Hosts: Los Angeles, Mexico City.
  - Controls with calendars: Chicago, Austin, Nashville, New Orleans.
  - Rounds:

    | round | Los Angeles | Mexico City | controls |
    |---|---|---|---|
    | December | 2025-12-04, before the 5 Dec draw | 2025-12-29 | Dec 2025 |
    | March | 2026-03-16 | 2026-03-30 | Mar 2026 |
    | June | 2026-06-15 | 2026-06-15 | Jun 2026 |

- **V2 — match-night spike.** Within each host snapshot, over T nights: `U_d = weekday FE + week FE + k·match_night`,
  with the same regression on controls' pseudo match nights as placebo.
- **V3 — booking timing.** Restricted to T nights after the June snapshot date (common to all rounds), the V1
  excess at December / March / June is expressed as fractions of its June value. These are the shares of excess
  event bookings made before December, December–March (about 1Q26) and March–June (about 2Q26). Nights before
  15 June carry no timing evidence and are assumed to follow the same split.
- **V3b — 2025 placebo.** For Los Angeles 2025-03-01 against controls' March 2025 snapshots, the same X statistic
  on the 2025 dates of T and A (minus 364 days) should be about 0.

## 6. Realised stays (reviews, descriptive)

V4. From `market_monthly_yoy.csv`, vintage-matched y/y for June and July 2026 minus March–May 2026, host markets
minus controls. Reported with n. Reviews lag stays, so July may be incomplete in the August dumps; stated, not
fixed.

## 7. Historical analog — Paris 2024 Olympics (A1)

Calendars with prices:

- Paris 2024-03-16, 2024-05-11, 2024-06-10.
- Rome 2024-03-22, 2024-05-17, 2024-06-15 (control).

Olympic nights are 26 July – 11 August 2024. Adjacent nights are 1–20 July and 16 August – 5 September 2024.

Statistics, as a DiD against Rome:

- The same-listing log listed-price premium, Olympic against adjacent nights.
- The unavailable-share excess, Olympic against adjacent nights.

It serves as a magnitude reference for what a mega-event did in this data type. It does not enter the translation.

## 8. Translation into the ADR line

effect_q (pp of global ADR) = 100 × Σ_host-metros [ N_T,m · f_q · r_m · π̄ ] / N_q,global.

| input | definition |
|---|---|
| N_T,m | Event-window stay nights in host metro m = Σ `estimated_occupancy_l365d` over the metro's 2026 listings × 39/365 × a summer factor. Factor: 1.0 central, range 0.9–1.3. |
| covered metros | The treated markets in §2 (lower bound). |
| scaled | × 104 / (matches at covered venues) (upper bound). |
| f_q | Share of those nights booked in quarter q, from V3. 4Q25 is the pre-December share plus the December-to-March share × 27/102 (days); 1Q26 is the rest of December–March; 2Q26 is March–June plus the June-to-tournament share. |
| r_m | Host-night ADR relative to global ADR: NA / global (US, Canada) or LatAm / global (Mexico), anchored regional levels for the base quarter from `data/processed/adr/04_regional_quarterly_wide.csv`. |
| π̄ | From P1. P2 is reported beside it, not substituted. |
| N_q,global | Airbnb booked nights in the quarter (2Q26 148.3m; 4Q25 121.9m). |

**Outputs**

- effect_4Q25 and effect_2Q26.
- The overstatement of the 4Q26 carried core: effect_2Q26 plus the 4Q25 comparison-base term (effect_4Q25).
- The implied 4Q26 ADR move, from the filed base $173.03 and the audit's consistent row.

Every output carries a low / central / high range from the product of the interval ends of π̄, the coverage bound
and the summer factor.

**Labels, fixed now.**

- *Measured composition term:* the low end of the 2Q26 effect is at least 0.10pp.
- *Direction only:* the central value is at least 0.10pp but the low end is below.
- *Not distinguishable from zero:* otherwise.

Whether the term enters the base is a human decision; this file only fixes the label.

## 9. Will not be done

- No specification, sample rule, window, threshold or market list changed after results.
- Every specification in §4–§7 is reported whatever it shows.
- No market dropped, other than by the §2 rules.
- No quote compared across price bases.
- No input chosen to reach the Street (DEC-0016).

## 10. Known limitations, stated before the results

1. Asking prices of unbooked inventory are not realised ADR. Booked event nights may have priced higher (booked
   early by high-willingness guests) or lower (hosts cut unsold asks) than the quotes we see.
2. "Unavailable" includes host blocks, and hosts may block around events.
3. Only two host metros have calendars; eleven more have one price snapshot; five host metros (Atlanta, Houston,
   Kansas City, Philadelphia, Guadalajara/Monterrey) and Miami-Dade proper are not in the data.
4. `estimated_occupancy_l365d` is Inside Airbnb's review-based model, not bookings.
5. Booking-date attribution uses snapshot dates that do not align with quarter ends.

## 11. Amendments before any result (22 Sep 2026)

Written while coding and before any outcome was computed. The hash of this file is re-logged after them.

1. **Central coverage.** §8 left the central coverage undefined. Central = the arithmetic mean of *covered* and
   *scaled*; low = covered; high = scaled.
2. **Dallas placebo.** The Dallas placebo cannot run under P2's own check-in ≤ 19 July rule: the snapshot was
   scraped on 20 July, so every quote checks in afterwards. It is dropped and reported as a design defect, not
   replaced.
3. **Common date set for V3.** V3's date set is T nights from 27 June 2026 (after the latest June snapshot,
   26 June) against the post-tournament A window only (24 July – 16 August). That is the only A window common to
   all three rounds. V1 stays literal (nights on or after s + 1 per market).
4. **Quarter split of the December-to-March interval.** Days are counted per host from its own snapshot dates:
   Los Angeles 4 Dec → 16 Mar (27 of 102 days in December); Mexico City 29 Dec → 30 Mar (2 of 91 days in
   December). Bookings after the June snapshot (15 June) are unobserved and get no weight, which understates f_2Q26.
5. **Timing and ratios per host.** US and Canadian host metros use Los Angeles's V3 timing; Mexico City uses its
   own. r_m uses the anchored regional ADRs of the quarter itself: 2Q26 NA 280.75 / global 183.73, LatAm 102.80;
   4Q25 NA 247.21 / 167.51, LatAm 95.51.
6. **V4 completeness rule.** A month enters only if the market's latest dump is at least 10 days after that month
   ends. Months are March–July 2026; pre is March–May, event is June–July.
7. **NYC.** NYC is a host by the §2 rule and is kept in N_T (the rule governs). Its share of N_T is reported
   separately because its quotes are 30-night stays.
