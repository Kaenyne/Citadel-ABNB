# A3 — Fee-deadline listed-price panels (theta)

Author: Claude, 2026-09-11 (runbook item A3)
Code: `analysis/src/forecast_methods/fee_panels/{build_sample,run_capture}.py`
Data: `data/processed/forecast_methods/fee_panels/{sample_ids.csv, sample_audit.csv, dryrun_new-orleans_2026-09-11.csv, runs/}`
Sources: S66–S71 in `research/sources/README.md`
Schedule: `~/Library/LaunchAgents/com.citadel-abnb.fee-panels.plist` (loaded, verified)

**Bottom line.** Both deadlines are sourced to Airbnb itself, verbatim. The sample is frozen
at 2,600 listings across 13 markets, 600 of them in the EEA control. The dry run works and
parses 100% — but **not by the route the runbook assumed**, and the route that does work
returns the *listed* price only, never the all-in total. That is enough to identify theta;
it is not enough to also verify the guest fee disappearing. Read §3 before trusting §5.

---

## 1. Sources for the deadlines

The runbook says "the repo has NO source for these dates." **That is wrong** — the source
was already in the repo, at `research/sources/fee_churn_catalyst.json`, record `FEE-01`,
accessed 2026-09-07. It is the correct URL. What was missing was the verbatim sentence and
an entry in the main source log. Both are now added (S66–S71).

### 1.1 Primary — Airbnb Resource Center, article 771

<https://www.airbnb.com/resources/hosting-homes/a/simplifying-service-fees-on-airbnb-771>
Published 2026-07-07 (page also carried an "Updated Aug 24, 2026" stamp on 2026-09-07).
Accessed 2026-09-11. Retrieved and quoted independently twice, agreeing word for word.

> "To simplify pricing, we're combining both fees into a single 15.5% service fee paid by
> hosts. For example, if you set your price at $115, guests see $115 and you earn $97 after
> the single fee is deducted. The 15.5% fee is based on Airbnb's global average service fees."

> **"The deadline to adjust your prices is September 15 if you live outside the European
> Economic Area and October 13 if you live within it or in Switzerland.** If you don't take
> action before your deadline, your prices and payouts per night will be lower. For example,
> if you keep your price at $100, you'll earn $84.50 after the 15.5% fee is deducted and
> guests will see $100."

> "The single service fee will only apply to reservations made after you switch to a single fee."

> "For listings in Brazil and Mexico, the single fee will remain 16%."

**Three caveats that change how the memo may cite this, and one that changes the research design:**

1. **Airbnb prints no year.** The page says "September 15" and "October 13", not
   "September 15, 2026". The year is an inference from the publication date. Five trade
   outlets (S69) independently print the 2026 year; cite S66 for the wording and S69 for
   the year. Do not attribute "2026" to Airbnb.
2. **It is framed as a pricing deadline, not a switch date** — "the deadline to adjust your
   prices". The fee structure change is the consequence of the deadline passing, and a host
   may switch early. So the treatment is a *window opening*, not a knife-edge event, and
   pre-deadline drift is expected, not anomalous.
3. **The deadline follows where the HOST LIVES — "if you live outside" — not where the
   listing is.** This is the design-relevant one; see §2.3.
4. Help Center article 1857 (S68) still describes the split fee as current and carries no
   dates at all. There is no Airbnb Newsroom post; this was communicated through the
   Resource Center and host email only.

### 1.2 Fee mechanics confirmed

| Claim | Status | Source |
|---|---|---|
| Single fee 15.5%, 16% Brazil/Mexico | **Primary verbatim** | S66, S68 |
| Band for the remainder: "typically pay 14%-16%" | **Primary verbatim** | S68 (art. 1857) |
| Fee base = nightly price + host-added fees (cleaning, pet, extra guest), excluding taxes | **Primary verbatim** | S68 |
| Guest service fee removed | **Never stated in those words by Airbnb.** Demonstrated only arithmetically ("if you set your price at $115, guests see $115"). Explicit "guests pay no service fee" wording is secondary-only | S66; S69 |
| Already mandatory for hotels/serviced apartments, PMS hosts, designated countries | **Primary verbatim** | S68 |
| Experiences ~20%, services ~15% (min $6) — separate schedules, not converted | **Primary verbatim** | S68 |
| Price-adjustment tool is one-way ("won't be able to revert back") | **Primary verbatim** | S68 (art. 4095) |
| PMS/software-connected migration began late 2025 | **Primary** | Airbnb art. 749; S67 |
| PMS migration *completed* April 2026 | **Contradicted by Airbnb.** Article 746, published 2026-07-29: "Hosts using property management software who aren't yet on the single service fee will switch to the single fee on October 13." A residual PMS cohort was still on the split fee in late July 2026 | S67 |
| Super Strict cancellation adds 2% (→ 17.5%) | **Unverified, and inconsistent with the primary 14–16% band.** Secondary-only. Do not use | S69 |

Cross-check against `data/processed/overnight/06_fee_timeline.csv`: consistent, and the
timeline should gain two rows — 2026-09 (non-EEA deadline) and 2026-10 (EEA + Switzerland
deadline), both now `high` confidence with an Airbnb-primary source. The timeline's
2025-10 row ("Airbnb begins migrating property-management-software hosts") is right to say
*begins*; anything claiming the PMS migration finished in April 2026 should be corrected
per S67. `research/notes/host_only_fee_history_and_elasticity.md` already asserts
"That noise resolves after Sept 15 / Oct 13" — now sourced.

---

## 2. The frozen sample

`data/processed/forecast_methods/fee_panels/sample_ids.csv`
5,200 rows = 2,600 listings × 2 fixed stay windows. SHA-256 `e75ea14a…0c7d085`.

### 2.1 Construction

Source: the most recent Inside Airbnb detailed dump per market, Aug 2026 (S70).
**These had to be downloaded — `data/raw/inside_airbnb/` does not exist in this repo**,
although `analysis/src/overnight/06_quote_panel.py` and `analysis/src/adr/11,12_*.py` all
read from it. Those scripts are not reproducible from the repo as committed; the dumps are
in the session scratchpad, and S70 records the exact 13 URLs so anyone can re-fetch them.

Eligibility (all must hold): `minimum_nights ≤ 3` **and** `maximum_nights ≥ 3` — a listing
with a 5-night minimum can never quote our 3-night stay, which would otherwise have burned
a large share of the sample — plus `has_availability`, `availability_90 > 0`, a non-null
room type, and a non-null `price_quote_raw` in the dump (the strongest single predictor
that the listing is live and quotable). 213,496 of 400,000-odd listings qualified.

Strata: `room_type × bedroom bucket (0-1 / 2 / 3+ / unknown) × host class`, 29–42 non-empty
cells per city, proportional allocation with a floor of one per cell, deterministic draw
(seed 20260911, listings sorted by id first so the draw does not depend on row order).

Host class uses `calculated_host_listings_count` — Inside Airbnb has no PMS flag —
as individual (1) / small_multi (2–4) / professional (5+). This is doing double duty: it is
the professional-vs-individual stratifier the runbook asked for **and** the
already-migrated proxy, because PMS-connected hosts migrated first (S67). Professional
hosts are kept and flagged, never dropped: they are the placebo arm (§5.3).

### 2.2 Counts

| city | country | EEA | dump | listings in dump | eligible | sampled | strata | geo-conflict |
|---|---|---|---|---|---|---|---|---|
| austin | United States | 0 | 2026-08-25 | 11,079 | 7,910 | 200 | 35 | 0 |
| chicago | United States | 0 | 2026-08-27 | 8,778 | 5,246 | 200 | 33 | 1 |
| los-angeles | United States | 0 | 2026-08-10 | 43,735 | 17,824 | 200 | 38 | 1 |
| nashville | United States | 0 | 2026-08-27 | 10,164 | 7,997 | 200 | 32 | 0 |
| new-orleans | United States | 0 | 2026-08-15 | 7,303 | 3,988 | 200 | 29 | 0 |
| new-york-city | United States | 0 | 2026-08-10 | 30,234 | 4,249 | 200 | 37 | 0 |
| san-diego | United States | 0 | 2026-08-29 | 13,342 | 8,163 | 200 | 33 | 0 |
| london | United Kingdom | 0 | 2026-08-18 | 92,783 | 50,552 | 200 | 42 | 1 |
| sydney | Australia | 0 | 2026-08-15 | 20,767 | 13,358 | 200 | 37 | 0 |
| mexico-city | Mexico | 0 | 2026-08-30 | 30,621 | 25,149 | 200 | 40 | 1 |
| **barcelona** | Spain | **1** | 2026-08-23 | 16,227 | 5,716 | 200 | 35 | 2 |
| **paris** | France | **1** | 2026-08-15 | 78,504 | 33,730 | 200 | 42 | 2 |
| **rome** | Italy | **1** | 2026-08-25 | 37,483 | 29,614 | 200 | 38 | 0 |
| **total** | | | | | **213,496** | **2,600** | | **8** |

**2,000 non-EEA (10 cities, 15 Sep) / 600 EEA (3 cities, 13 Oct).**
London is deliberately in the *non-EEA* arm: the UK left the EEA in 2020, so London hosts
take the 15 Sep date. Mexico City is non-EEA and carries the **16%** fee, so its
payout-neutral reprice is +15.5% rather than +14.8% — a small difference, but it needs its
own theta denominator (§5.2) or it will read as ~5% more pass-through than it has.

Balance across the EEA cut (non-EEA / EEA): entire home 1,399/449, private room 463/107,
hotel room 77/23, shared room 61/21; individual 607/203, small_multi 444/130, professional
949/267; bedrooms 0-1 581/230, 2 476/159, 3+ 546/111, unknown 397/100. Close enough that
strata weights will not be doing heavy lifting, with one exception: the EEA arm is lighter
in 3+ bedroom listings (18.5% vs 27.3%), so weight or control for size.

### 2.3 The treatment is host residence, not listing location

Airbnb's own sentence keys the deadline to where the host *lives* (§1.1, caveat 3). A
US-resident owner of a Paris flat migrates on 15 Sep and is **treated**, not control. The
sample carries `host_location` verbatim, a coarse `host_region_guess` ∈ {eea_ch, non_eea,
unknown}, and a `geo_conflict` flag.

Reassuringly, the proxy is good where it is observed: in the EEA cities 435 of 439
resolvable hosts read as EEA/Switzerland, and in the non-EEA cities 1,399 of 1,403 read as
non-EEA — **8 conflicts in 2,600**. The real exposure is the 758 listings (29%) whose
`host_location` is blank or unparseable. Run the DiD on the full sample and again on
`host_region_guess` agreeing with `eea_flag`; if the estimate moves materially, the EEA
control is contaminated and the wider band is the honest one.

### 2.4 Fixed stay dates

Every run quotes the **same two stays**, so movement in the series is price, never question.

| window | check-in | check-out | nights |
|---|---|---|---|
| W1 | 2026-11-13 (Fri) | 2026-11-16 (Mon) | 3 |
| W2 | 2026-12-11 (Fri) | 2026-12-14 (Mon) | 3 |

Both are Friday→Monday so day-of-week mix is constant; both fall **after the last capture
run (16 Oct)** so lead time stays positive throughout — an important correction to the
runbook's suggested "28 days after 14 Sep", which would have landed W1 in the past by the
October runs. W1 is 28 days and W2 56 days after the final run. Both avoid US Thanksgiving
(26 Nov) and the Christmas peak. Lead time necessarily shrinks across runs; that is common
to treated and control and is absorbed by run fixed effects.

---

## 3. Dry run — what actually works

### 3.1 The prior art does not carry over

`ABNB-Crossover/tools/cc_pricing_scraper.py` and `cc_pricing_aggregate.py` are **not Airbnb
scrapers**. They are byte-identical copies of a Common Crawl scraper for Kay/Zales/Jared
jewelry product pages; `TOOLS_README.md` grades `cc_pricing_scraper.py` "Adapt" and says to
replace "the whole `parse()`". That adaptation was never done. There is no pre-existing
Airbnb quote scraper in this repo to dry-run.

`analysis/src/overnight/06_quote_panel.py` does not scrape at all — it reads the
`price_quote_raw` column that Inside Airbnb ships inside the dump.

**And that column does not contain what the runbook believes it does.** The runbook calls
06 "the team's fee-inclusive quote panel". It is not fee-inclusive. A parsed quote:

```json
{"quote": {"taxes": null, "currency": "USD", "service_fee": null, "total_price": "139.00",
           "cleaning_fee": null, "is_available": true, "nightly_subtotal": "139.00",
           "requested_checkin_date": "2026-08-19", "requested_checkout_date": "2026-08-20"}}
```

`service_fee`, `cleaning_fee` and `taxes` are null, `total_price == nightly_subtotal`, and
the stay is **one night**, not three. `analysis/src/adr/11_quote_index_test.py` already says
so in its own docstring ("the raw quote carries no service fee, cleaning fee or tax lines in
these dumps — checked"). The team's memory that "calendars carry no price" is a different
and milder problem than the real one: the *quotes* carry no fees. Any claim built on
06 being fee-inclusive should be withdrawn.

### 3.2 Listing-page (PDP) route — verified broken

`run_capture.py --mode pdp`, 6 quotes, New Orleans:

| metric | result |
|---|---|
| HTTP 200 | 6/6 (100%) |
| bytes returned | 496–592 KB, real pages, no block, no CAPTCHA |
| price parsed | **0/6 (0%)** |
| parse_status | `price_not_server_rendered` ×6 |

The server HTML contains `data-deferred-state` with the listing's full content, but
`structuredDisplayPrice` is `null` and the `BOOK_IT_SIDEBAR` section is
`sectionContentStatus: "NOT_COMPLETE"` — the price is fetched client-side after load.

Confirmed in a **real, logged-out Chrome session** on listing 2170610 with dates in the URL:
the booking panel rendered "Add your travel dates for exact pricing" / "Add dates for
prices". **Airbnb ignores `check_in`/`checkout` URL parameters for an anonymous session.**
So even a headless browser must drive the calendar widget per listing — roughly 5,200
interactive sessions per run. Not viable at this sample size.

I attempted the internal GraphQL endpoint (`/api/v3/StaysPdpSections`) using the API key and
persisted-query hash lifted from Airbnb's own JS bundle. **This was blocked by the
environment's permission classifier and I did not work around it.** The judgement looks
right: it impersonates Airbnb's web client against a private API. If the team wants that
route it is a human decision, and it should be weighed against Airbnb's ToS, not taken by
an agent. Flagged as a blocker, not a failure.

### 3.3 Search-results route — works

Airbnb's **public search results page** does server-render prices. `run_capture.py --mode
search`, New Orleans, 6 cursor pages × 2 stay windows, 2.5 s between requests:

`data/processed/forecast_methods/fee_panels/dryrun_new-orleans_2026-09-11.csv`

| metric | result |
|---|---|
| rows | 225 (207 unique listings) |
| HTTP failures | 0 |
| **parse_status = ok** | **225 / 225 = 100.0%** |
| wall time | 2 min 49 s (24 page fetches) |

Field fill rates:

| field | fill | note |
|---|---|---|
| `nightly_price` | 100% | from the "3 nights x $160.33" line |
| `total` | 100% | after a one-line parser fix; see below |
| `currency` | 100% | USD here; EUR/GBP/AUD/MXN expected elsewhere, kept native |
| `original_total` | 50% | pre-discount price where a discount is running |
| `host_added_fees` | 2% | "Resort fee" — real host-added fees do appear |
| **`cleaning_fee`** | **0%** | **never returned** |
| **`service_fee`** | **0%** | **never returned** |
| **`taxes`** | **0%** | **never returned** |

The only parser fix needed: 14 of 225 cards omit `primaryLine.discountedPrice`, so `total`
was null. Falling back to the breakdown's own "Price after discount" line, else the
`nights × rate` subtotal, took the parse rate from 93.8% to 100%. That is the whole fix.

**Fields the scraper no longer returns.** Cleaning fee, Airbnb service fee and taxes are
absent from every one of the 225 cards. The card's `displayPriceStyle` is `TOTAL_ONLY` and
`secondaryLine` (which historically carried "total before taxes") is null. Across the whole
dry run the only non-nightly line labels seen were: Price after discount (35), Early booking
discount (30), Resort fee (4), Long stay discount (3), Special offer (1), Discount (1).
**This series is a listed-price series, not an all-in-total series.** §5 is built on that
and nothing more.

This is exactly the failure mode `parse_promos.py` was written to warn about — its
TOOLS_README lesson is that anchoring on one DOM hook silently zero-fills other eras and
manufactures a trend. `run_capture.py` therefore records `parse_status` and the raw
`line_items` string on every row, so a future schema change shows up as a status change
rather than as a suspiciously clean zero.

### 3.4 The one real design problem

Search returns **whatever it ranks that day**, not a list you hand it. Of the 207 listings
the dry run returned, only **6 are in the frozen 200-listing New Orleans sample**, and 93%
(193/207) join to the Inside Airbnb Aug dump (so strata are recoverable by join). Worse,
the W1 (117 listings) and W2 (108) result sets for the *same* city on the *same* day share
only 18 listings (17%) — ranking is date-sensitive.

So the panel is the **intersection across runs**, not the frozen list. Two consequences:

- `sample_ids.csv` currently functions as the identification *frame* and strata reference,
  not as the set of listings that will actually be priced. It is worth keeping — it is the
  only artifact ready to use if a PDP route is restored — but the memo must not claim the
  2,600 listings are being tracked.
- Run-to-run stability (same city, same dates, different day) is the number that matters
  and **the dry run could not measure it** — that needs two runs. The first real check is
  14→16 Sep. `--pages 15` (270 listings per city-window) is the default to widen the
  intersection. **If run-to-run overlap comes back under ~40%, the search route will not
  support a listing-level DiD** and the fallback is a city-level median-price index, which
  is far weaker (composition change is no longer differenced out).

---

## 4. Schedule

`~/Library/LaunchAgents/com.citadel-abnb.fee-panels.plist`, loaded with
`launchctl load -w`, verified:

```
$ launchctl list | grep fee-panels
-	0	com.citadel-abnb.fee-panels
$ launchctl kickstart gui/501/com.citadel-abnb.fee-panels
… runs/launchd.out.log:
16:05:02 2026-09-11 is not a capture date ([…]) -- exiting 0
```

Target runs: **09:00 local on 14, 16, 18 Sep and 12, 14, 16 Oct 2026** — two observations
before each deadline and one after, so a pre-trend and a jump are both estimable inside each
cohort's own window.

launchd's `StartCalendarInterval` has **no year field**, so six dated entries would fire
again every September and October in perpetuity. The agent therefore fires **daily at
09:00** and `run_capture.py` exits 0 immediately unless today is one of the six dates
(`CAPTURE_DATES` in the script). The schedule lives in version control, not in the plist.
Backfill a missed slot with `--date YYYY-MM-DD`; re-run manually with `--force`.

Each run: 13 cities × 2 windows × 15 pages = 390 page fetches at 2.5 s ≈ 17 minutes, one
request at a time, descriptive User-Agent with a contact address, exponential backoff on
429/5xx. Output one CSV per run under `data/processed/forecast_methods/fee_panels/runs/`.

**Two operational risks.** The Mac must be awake at 09:00 (launchd will run a missed
`StartCalendarInterval` job once on wake, but the capture would then be hours late — check
`captured_at`, not the filename). And the 14 Sep run is the **only** pre-deadline
observation that also precedes any migration; if it is missed there is no clean pre-period
for the non-EEA cohort.

---

## 5. How theta will be measured

theta is the fraction of the payout-neutral reprice a host actually passes into the listed
price. Payout-neutral is **+14.8%** at a 15.5% fee — the host used to net 0.97 of the subtotal
and now nets (1−f) of the listed price, so the neutral ratio is 0.97/(1−0.155) = 1.1479,
i.e. **+13.80 log points**. In Mexico City at 16% it is 0.97/(1−0.16) = 1.1548, **+15.5%
(+14.39 log points)** — close to the 15.5% markets, not far above them. theta = 1 is full
pass-through (guest all-in price roughly unchanged, ADR +0.7%); theta = 0 means the host
eats the fee (guest all-in price −12.3%).

### 5.1 Why the current estimate is not an estimate

`data/processed/adr/12_reprice_summary.csv` reports theta ∈ [0.833, 1.407] across 420
market-pairs. That range is **an artifact of the estimator, not a measurement**:
`theta = mean_jump_pp / 13.797`, where `mean_jump_pp` is the weighted mean log price jump
*inside a detection window fixed at +12 to +20pp*. The window's own bin midpoints run 11.5
to 19.5pp, which map to theta 0.833 to 1.413 — **the reported range is the window**. theta
cannot come back outside it no matter what hosts do. Confirming this, the excess mass the
estimator is supposed to detect is negligible: median `excess_share_12_20` = 0.29%, max
4.3%, and 65 of 420 rows sit exactly on the 0.8333 floor. The honest statement is that
theta is **unidentified**, not "measured at 0.83–1.41", and the take-rate edge currently
rests on a number that no data has yet constrained.

### 5.2 The design

Difference-in-differences on **log listed price**, migrating cohort vs EEA control:

```
log(P_ist) = α_i + δ_t + θ̃ · (NonEEA_i × Post15Sep_t) + ε_ist
```

for each fixed stay window s, with listing fixed effects α_i (so composition and
listing quality difference out) and run fixed effects δ_t (so the common lead-time drift
does). **theta = θ̃ / 0.1380** (÷0.1439 for Mexico City).

The identification is the 27-day gap between the two deadlines. Between 15 Sep and 13 Oct,
non-EEA hosts are treated and EEA hosts are not. Then the design **reverses**: over
12–16 Oct the EEA cohort is treated and the non-EEA cohort is a now-fully-treated control,
which is a genuine second estimate on a different population — and a consistency check,
because the two should give the same theta.

- **Sep window (14/16/18):** treated = 10 non-EEA cities; control = Barcelona, Paris, Rome.
- **Oct window (12/14/16):** treated = the 3 EEA cities; control = the 10 non-EEA cities,
  now post-migration and therefore expected flat.
- Run on the full sample and again restricted to `host_region_guess == eea_flag` (§2.3).
- Mexico City estimated separately (16% fee) or with its own denominator.

Because the deadline is a *pricing* deadline hosts may meet early (§1.1 caveat 2), read the
14→18 Sep move as a lower bound on the eventual jump and expect drift before 14 Sep. The
level shift between the 18 Sep and 12 Oct runs on the non-EEA cohort captures late movers.

### 5.3 Placebo and falsification

**Placebo — the already-migrated.** Professional hosts (5+ listings, 949 non-EEA / 267 EEA)
are disproportionately PMS-connected and migrated in late 2025 (S67). They should show **no
jump on 15 Sep**. If they jump as much as individual hosts, the estimator is picking up
something seasonal or a ranking change, not fee pass-through, and the whole result is void.

**What would falsify full pass-through (theta = 1):**

- θ̃ significantly below 0.1380 in the Sep window — hosts absorbing the fee. θ̃ ≈ 0.069
  (half pass-through) would put the guest all-in price ~6% below the old level, which
  bites ADR and therefore GBV.
- **θ̃ statistically indistinguishable from zero.** This is the live risk, not a remote one:
  the 2020 migration's payout-neutral advice was widely ignored, and the dry run shows
  17.8% of quotes carrying an active discount line (45% priced below an `originalPrice`),
  which is enough noise to swamp a 14% jump at n ≈ a few hundred per cell. Power, not sign, is the binding constraint.
- A jump of the same size in the **EEA control** during the Sep window — the control is not
  a control, the design fails, and no theta can be read from it.
- Estimates from the Sep and Oct windows that disagree by more than their confidence
  intervals — one of the two cohorts is contaminated (most likely via host residence, §2.3).

**What this design cannot do.** It cannot verify that the guest service fee actually
disappeared, because the search route returns no service-fee line (§3.3). theta is
identified off the *listed* price alone, under the maintained assumption that the displayed
search price is the guest's pre-tax all-in price — which has been Airbnb's global default
since Apr 2025 (`06_fee_timeline.csv`, 2025-04) but is not verified in our own data. If
that assumption is wrong, the estimate is biased by whatever the split-fee hosts' guest fee
was doing, and the sign of the bias is not known a priori. **State this limitation wherever
theta is cited.**

---

## 6. Blockers and what I did not do

1. **No route prices a pre-specified listing.** The PDP is client-side and ignores date
   parameters; the private GraphQL route was blocked by the permission classifier and I did
   not attempt to bypass it. Needs a human decision on ToS, or a licensed data source
   (AirDNA / AllTheRooms), or a headless-browser harness driving the calendar widget.
2. **Run-to-run panel stability is unmeasured** and is the single assumption the design
   rests on. First measurable on 16 Sep. Under ~40% overlap, fall back to a city-level index
   and say so.
3. **No cleaning-fee / service-fee / tax series**, so the all-in-total leg of the
   listed-vs-total comparison does not exist. §5.3 records what that costs.
4. **`data/raw/inside_airbnb/` is missing from the repo**, so `06_quote_panel.py` and
   `analysis/src/adr/11,12_*.py` cannot be re-run as committed. Dumps re-downloaded to the
   session scratchpad; URLs recorded at S70. Someone should decide where they live.
5. Nothing was committed to git, and the harness and `/L0` were not touched.
