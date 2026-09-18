# RNPL research handoff — start here

**Owner:** Krish. **Research date:** September 10, 2026. **Work:** original H1/H2 exploration with Claude, followed by RNPL source/forecast audits, materiality calculations, and a calendar pilot with Codex and bounded Terra/Luna reviews.

## Research question and current position

Our starting question was whether Reserve Now, Pay Later lets guests make more tentative reservations, inflating forward bookings and reducing eventual conversion, and whether its staggered rollout and anniversary can affect Q3/Q4 2026 reported nights. The working Q3 growth anchor was roughly 10%. This is a hypothesis to investigate, not a conclusion that RNPL destroys demand or causes a forecast miss.

We have established useful definitions, public rollout anchors, materiality thresholds, and reproducible calendar diagnostics. **We have not estimated an RNPL-specific cancellation rate, its incremental Q3/Q4 loss versus the forecast, or an RNPL/no-RNPL causal effect. No cancellation haircut was applied to the live model.**

Read inconclusive results conservatively. A weak relationship in this particular series, a missing label, small sample, calendar gap, or changing panel can conceal a real effect. None of the approaches below is declared permanently unproductive. Record what a test can and cannot identify, and what additional evidence would make it informative.

## Reading order for a teammate or their AI

1. **This handoff:** scope, findings, limits, and open paths.
2. [Forecast/source/data audit](../outputs/rnpl-audit-20260910/research-pass.md): how the approximately 10% numbers were constructed; rollout; data feasibility; minimum reservation-data request.
3. [Conversion framework](../research/notes/2026-09-10_rnpl-conversion-framework.md): stock-versus-flow distinctions, equations, cohort design, and alternative measurement paths.
4. [Materiality tables](../outputs/rnpl-audit-20260910/materiality.md): losses and probability revisions needed for a 1–3-point growth effect. All exposures/hazards are scenarios.
5. [Calendar pilot report](../outputs/rnpl-calendar-pilot-20260910/pilot-report.md): actual measured availability transitions, denominator counts, retention, screening, fixed horizons, and reclosure.
6. [Original H1/H2 bridge](../research/notes/2026-09-10_h1-to-h2-bridge.md): preserved exploratory context. Its RNPL attribution and haircut are not validated by the later work; read the status notice first.

## Definitions that must survive the handoff

- **Reported Nights and Seats Booked:** bookings recorded in the quarter minus cancellations and alterations recorded in that quarter, including cancellations of earlier bookings. It includes seats; a stays-only panel is not the full KPI.
- **Completed nights / revenue:** a different time basis. Revenue is principally recognized around check-in; a booking-date model needs a timing bridge to a stay-date outcome.
- **Backlog survival:** conditional survival of reservations still live at a stated snapshot date. Do not apply an original lifetime cancellation probability to an already-surviving cohort.
- **RNPL anniversary:** a product-driven level increase can stop contributing to year-over-year growth without any deterioration in conversion.
- **Cancellation tail:** earlier booking cohorts can create later-quarter cancellation recognition. This can coexist with a genuine net booking or completed-stay benefit.
- **Calendar reopening / reclosure:** unavailable→available / unavailable→available→unavailable for identical listing/stay dates. Neither establishes a cancellation or a replacement booking.

## What we learned, with evidence status

### Public disclosures and forecast reconstruction

US RNPL began during Q3 2025; the August 14 announcement is not necessarily the treatment start. Initial eligibility was US guests booking eligible domestic stays with flexible/moderate policies. Approximately 70% take-up refers to those offered the product, not platform-wide penetration. Global eligible domestic/international availability was announced February 17, 2026. The announcement has currency exceptions, so country alone is not exact treatment assignment.

Management described roughly 20% of Q1 GBV from RNPL. GBV share is not nights share, eligibility share, or outstanding-backlog share. Q2's over-20% GBV and July expansion of eligible booking types were recovered from call transcript mirrors; the official Q2 letter corroborates broader expansion but not those exact details. Keep that source distinction.

The approximate 16% historical versus 17% aggregate cancellation comment is not a quarterly, night-weighted RNPL cohort series. Management also said mature tested cohorts were net beneficial and cancellations tracked tests. Both statements matter: a higher cancellation propensity does not prove the product has negative economics, and management's testing commentary does not eliminate forecast-timing risk.

**Important correction:** Q1's approximately 3 points nights / 4 points GBV growth was attributed to RNPL, cancellation-policy changes, and simplified fees combined. The original bridge treated it as RNPL-only/US-only in places. Preserve the original exploration, but do not carry that attribution forward.

The existing approximately 10% forecasts target reported net nights. The seasonal bridge gives 9.49% Q3 before overlays, or 9.99% after an assumed 0.5-point World Cup benefit. A separate naive baseline carries forward Q2's 10.34%. Two weak demand-index variants give 9.95%/10.01%; another composite gives 11.84%. These are not four independent observations of gross demand. The original -1.5/-2.5-point RNPL overlay has no fitted exposure or cancellation curve.

The original bridge also uses strong language about historical causes and paths that did not appear material. Its projections, causal explanations, and negative research judgments remain exploratory, including broader revenue/event claims outside this RNPL audit. Preserving the original text is not endorsing those claims or excluding regulation, events, alternative data, or other mechanisms from further research.

The saved public-consensus file did not contain a nights consensus. “10–12” is a researcher mapping of management's qualitative low-double-digit wording. Related team PR #32 cites a separate approximately 10.2% consensus; reconcile its source and date rather than assuming consensus is unavailable everywhere or that the mapping is a literal company range.

### Materiality arithmetic

With 2025 reported denominators fixed, a one-point growth revision requires **1.336 million Q3** or **1.219 million Q4** net lost nights versus the forecast. Two points requires 2.672/2.438 million. These are arithmetic thresholds, not estimated losses.

At an illustrative 40 million live RNPL nights, a one-point Q3 haircut needs a 3.34-point upward revision to the probability of cancellation during Q3, beyond risk already assumed; with a 25% incremental same-quarter net rebooking offset, it needs 4.45 points. We have not measured the 40 million exposure, probability revision, or offset. Do not treat H1 gross RNPL bookings as live September exposure.

### Calendar pilot

Selected Austin, Rome, and Sydney before viewing outcomes: five vintages each and Europe/APAC comparisons alongside the US. Fully read 15 files, sampled approximately 10% of listing IDs deterministically, and followed the same IDs across vintages. Matched exact future listing/stay dates; omitted elapsed dates and did not infer outcomes for missing listings.

Short-run reopening, March→June versus June→August: Austin **10.2%→10.0%**, Rome **9.0%→13.3%**, Sydney **9.4%→7.7%**. Rome's increase also appears in each of the first three fixed days-to-arrival bands. This is a descriptive lead for independent verification, not an RNPL attribution or a clean temporal change: seasons, interval lengths, initial reservation ages, and mix differ.

Broad reopening rates are much higher than short-run rates. That demonstrates sensitivity to the definition of unavailable inventory, not proof that every excluded long run is a host block or that the stricter estimate is correct. Among short-run dates that reopened March→June and remained observable through August, approximately **32–44% reclosed**. That is not a measured rebooking offset.

December→March retained only approximately **51–63% of initially unavailable future dates** across these markets. Results condition on the surviving panel. The all-five-vintage sample also introduces look-ahead/survivorship; it is a robustness description, not a historical forecast backtest. Raw files begin after US rollout and supply no 2024 baseline.

## What worked, what remains inconclusive, and how to revisit it

| Path | What worked / actual limit in this pass | Why the research path remains open | Useful next evidence |
|---|---|---|---|
| Disclosure chronology | Separated rollout, eligibility, adoption, GBV share, product bundle | Exact rollout percentages and cancellation lags are undisclosed, not zero | Official call PDF/audio, IR clarification, contemporaneous eligibility evidence |
| Historical H1/H2 bridge | Reproduced reported-net-nights baseline and isolated assumed overlays | Three historical transitions, product changes, and rounding do not identify RNPL | Broader cohort model, explicit rollout exposure and two-year timing bridge |
| Cash balances / unearned fees | Clear payment-timing confound; useful consistency constraint | Cannot isolate cancellation from deferral alone; still may help jointly identify exposure | Payment schedule, fee mix, booking-age distribution, funds-release timing |
| Lagged GBV→revenue conversion | Gives an aggregate historical bridge | Booking lead times, ADR/take-rate mix, and cancellations can all change it; poor residual fit need not mean poor demand | Distributed booking-to-stay lags, cohort GBV/revenue, fee and FX adjustments |
| Single calendar snapshots | Useful inventory/horizon description | Lack of transitions is a dataset limitation | Repeated identical listing/stay-date observations |
| Repeated calendars | Exact-key reopening/reclosure is feasible, with measured screening and retention sensitivity | Sparse captures miss cancel-and-refill; host blocks and guest origins unobserved | Higher-frequency history, corroborating PMS events, better classification, origin/policy labels |
| Short unavailable runs | Creates a narrower comparison and reduces broad reopening levels | Short runs can still be blocked; real long bookings are excluded; cohort selection can alter rates | Validate run classification against known reservations; vary caps and boundary rules |
| Rome descriptive increase | Survives basic days-to-arrival slicing | No matched-season/equal-interval baseline or RNPL labels; exploratory selection needs independent confirmation | New holdout period, comparison markets, reservation-level cancellation histories |
| Regional rollout comparison | US/global timing offers potential variation | Destination is not guest origin, macro/policy changes overlap, US prelaunch missing here | Origin×destination×policy×booking-age cohorts; pretrend tests |
| Reviews / official stayed-night series | Possible realized-demand cross-check | Review propensity, party size, length of stay, geography and platform coverage differ; weak tested links need not imply no signal | Stable matched panels, correct release vintages/lag, conversion to comparable night units |
| Existing macro/alt-data models | Multiple nowcasts/backtests are preserved elsewhere | Small changing samples, common trends, publication timing and measurement can explain weak performance | Revisit with better coverage and out-of-sample validation; do not label all alt data ineffective |

No route is falsified by the present absence of an identified RNPL coefficient. Conversely, do not force any proxy to fit the desired haircut. Keep a record of exclusions, missingness, alternative explanations, and what would weaken as well as support the hypothesis.

## Outstanding ideas and recommended next steps

1. **Reservation-data feasibility sample:** ask a property manager/channel manager what event fields actually exist before requesting a large export. Need anonymized reservation/listing ID, channel, creation date, original/revised nights and stay dates, cancellation date/reason/nights, original policy, extraction cutoff, and panel membership. Guest origin/currency and RNPL offered/chosen/payment dates are especially valuable. Host payout date is not guest payment date. No outreach has been sent.
2. **Validate the calendar classification:** link a small known-booking sample to calendar runs; quantify false positives/negatives rather than assuming unavailable=booked. Higher-frequency historical captures may reduce missed churn. New collection cannot retroactively repair missing US prelaunch history, but can help subsequent quarters.
3. **Independently check Rome:** match season, observation length and lead-time distribution; retain Austin/Sydney or other preselected comparisons. Do not treat Rome as established simply because it was the strongest pilot result.
4. **Model cohort survival and timing:** distinguish original cohort cancellation probability from remaining risk; allow newly eligible mix to differ; handle right censoring. Build booking-month×cancellation-month and booking-month×stay-month matrices, including within-quarter new booking flow and replacement bookings.
5. **Reconcile the forecast counterfactual:** establish what each starting model embeds. Model 2025 and 2026 separately for an RNPL/no-RNPL comparison; use a fixed 2025 denominator only for a revision to the existing 2026 forecast. Separate product level/anniversary, pull-forward, and cancellation tail.
6. **Broaden coverage when useful:** extending to 34 markets is possible. It could reveal geography or robustness, but more of the same fields alone will not isolate RNPL. Do not close this path; define the incremental question first.

Other live ideas: guest payment-deadline failure hazard; RNPL night share from GBV/ADR with matched denominators; longer backlog residence increasing exposure; initial booking uplift versus lower survival; original-property loss versus guest platform rebooking; policy changes independent of RNPL; negative controls based on ineligible currencies/policies after verifying historical rules. These were proposed, not tested to rejection.

## Artifacts and reproducibility

| Artifact | Purpose |
|---|---|
| `analysis/src/h1_to_h2_bridge.py` and `data/processed/h2_bridge/` | Original exploratory bridge and saved outputs; caveats in directory README |
| `data/raw/fred/DTWEXBGS.csv`, `DEXUSEU.csv` | Small public FRED inputs for that original bridge; retained September 10 vintage |
| `analysis/src/rnpl_materiality.py` | Regenerate thresholds and illustrative exposure scenarios |
| `outputs/rnpl-audit-20260910/` | Audited interpretation, calculations, historical calendar inventory |
| `analysis/src/rnpl_calendar_pilot.py` | Deterministic sample, exact future-date joins, screens and three-capture diagnostics |
| `analysis/src/rnpl_calendar_pilot_report.py` | Regenerate the readable report and check manifest URL/size alignment |
| `outputs/rnpl-calendar-pilot-20260910/{austin,rome,sydney}.json` | Saved aggregate results, denominator counts and source hashes/URLs |
| `data/processed/adr/14c_calendar_manifest.csv` and `analysis/src/adr/14c_los_runs_panel.py` | Existing acquisition manifest and download code for historical calendars |

Run from the repo root with Python plus pandas/numpy (the repository requirements list dependencies):

```text
python analysis/src/rnpl_materiality.py
python analysis/src/rnpl_calendar_pilot.py --self-test
python analysis/src/rnpl_calendar_pilot_report.py
# Full pilot: requires the 15 raw calendar files described below.
python analysis/src/rnpl_calendar_pilot.py
python analysis/src/rnpl_calendar_pilot_report.py
# Original exploratory bridge; writes its legacy output directory.
python analysis/src/h1_to_h2_bridge.py data/raw/fred
```

The report and materiality steps work from committed results/inputs. Raw calendar archives are large and gitignored; this PR includes their aggregate results and provenance, not the archives. On Krish's machine they are under `data/raw/inside_airbnb_calendar/`. To recreate, read the exact 15 URLs and expected SHA-256/byte sizes from the market JSONs, acquire those source files into the recorded paths, and verify before recomputing. Existing acquisition code documents the download procedure; do not blindly launch a 164-file acquisition for this three-market pilot. If a URL no longer serves that vintage, record an acquisition gap and obtain the archived file from the team. Do not treat missing raw data as a failed replication of the economic hypothesis.

Validation: pilot full run succeeded on all 15 files; synthetic elapsed/unmatched/transition checks passed; sampled duplicate/availability and one-to-one join checks passed; report checked all 15 manifest URLs/sizes; materiality checked denominators and arithmetic identities. This validates implementation/provenance checks, not causal identification. Re-running the full pilot is only necessary if inputs or analytical code change.

## Parallel work and boundaries

- [PR #32, Quarterly nights path: put the three-feature lap on real quarters](https://github.com/Kaenyne/Citadel-ABNB/pull/32): related product-lap model. Its growth residual allocation is a separate model assumption, not a reservation-cohort RNPL estimate. Reconcile international rollout, consensus provenance, and bundle attribution before combining models.
- Remote branch `jessie/backlog-conversion` existed when this handoff was packaged. It contains related backlog-conversion work; it was not merged or audited as part of this package. Inspect it before duplicating that effort or assuming agreement.
- Earlier context already on main: [RNPL factor note](../research/notes/2026-09-05_austin-str-rnpl-hotel-factors.md), [EU/backlog analysis](../research/notes/2026-09-05_eu-platform-and-backlog.md), [alt-data backtests](../research/notes/overnight/08_altdata-index-and-backtests.md), [macro/alt-data nowcast](../research/notes/predictive/03_macro-altdata-nowcast.md). Their negative wording describes those tests/data, not permanent closure of a research path.
- This publication adds the RNPL research and original bridge context. It does not change live workbook assumptions, adjudicate the broader revenue thesis, or publish raw licensed terminal exports, private files, raw calendar dumps, or unrelated working files.

## Suggested prompt for the next AI

> Read `docs/RNPL_HANDOFF.md`, then the linked audit and pilot report. Continue investigating whether RNPL changes remaining booking survival and reported Q3/Q4 nights. Separate sourced facts, descriptive results, assumptions, and causal claims. Treat inconclusive paths as potentially data-limited, not disproven. Do not infer bookings from unavailable dates, use reclosure as confirmed rebooking, or apply a lifetime cancellation rate to a net-nights forecast. First state what the proposed next test can identify, the data required, and how it will distinguish RNPL from competing explanations. Preserve evidence that supports and weakens the hypothesis, and reconcile parallel team work before combining estimates.

