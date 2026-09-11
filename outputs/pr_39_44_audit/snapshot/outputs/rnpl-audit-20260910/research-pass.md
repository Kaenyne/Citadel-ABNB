# RNPL research pass: forecast audit, rollout, materiality, data feasibility

As of September 10, 2026. Scope: steps 1–4, using existing research/data and public disclosures. The forecast and data audits were delegated to GPT-5.6 Terra and Luna; the source audit to Terra. The parent reconciled findings and generated materiality calculations. Existing forecasts have not been changed.

## Decision

The available work does not establish an incremental RNPL cancellation haircut. The approximately 10% forecast targets reported net Nights and Seats Booked, not gross RNPL reservations awaiting their first cancellation adjustment. Its historical inputs already include cancellations recognized to date, but do not explicitly forecast an RNPL cancellation tail.

There is enough local historical calendar data for a small reopening-proxy feasibility pilot, alongside a narrow reservation-data field request. A broad new calendar scrape or a 1.5–3 point base-case haircut is not justified. The hurdle is concrete: an additional 1.336 million net lost nights reduces Q3 growth by one point, and 1.219 million does the same for Q4. The task is to demonstrate those losses relative to the existing forecast, with timing and replacement bookings accounted for.

## 1. Reconciliation of the approximately 10% forecast

| Existing calculation | Q3 2026 | Q4 2026 | Interpretation |
|---|---:|---:|---|
| H1 average plus 2023–25 mean seasonal transition | 9.492% | 10.618% | Descriptive reported-net-nights model; three historical transitions |
| Same model, no RNPL lap, with +0.5-point World Cup overlay in Q3 | 9.992% | 10.618% | Source of the bridge's approximately 10%; the World Cup overlay is an assumption |
| Carry forward Q2's reported growth | 10.342% | — | Naive baseline in the alt-data work |
| Demand index excluding Inside Airbnb / post-2022 composite variant | 9.951% / 10.008% | — | Separate weak models, not an independent measured gross-booking series |
| Full demand composite | 11.844% | — | Shows model-selection uncertainty; cannot present only the roughly 10% variants as agreement |
| Existing bridge after assumed RNPL lap | 8.492% | 8.118% | Subtracts 1.5 / 2.5 points without a cancellation model |

Reproduction: Q1/Q2 2026 reported growth inputs are 9.15% and 10.34%, averaging 9.745%. Mean historical Q3 transition is -0.2533 points; Q4 is +0.8733. Exact stored variants differ slightly in rounding of historical volume growth, not economic interpretation.

Sources within the repository:

- `analysis/src/h1_to_h2_bridge.py`, especially method lines 5–11, baseline lines 211–224, overlays lines 236–252, scenarios lines 267–281.
- `data/processed/h2_bridge/h2_bridge_transitions.csv`, `h2_bridge_2026_projection.csv`, `h2_bridge_nights_scenarios.csv`.
- `data/processed/overnight/08_q3_2026_nowcast.csv`; `analysis/src/overnight/08_altdata_backtests.py`, lines 504–530.
- `research/notes/overnight/08_altdata-index-and-backtests.md`; `research/notes/predictive/03_macro-altdata-nowcast.md`.

Airbnb defines the KPI as booking-period nights and seats net of cancellations and alterations in that period. Thus historical net growth embeds past cancellation recognition, not necessarily the risk remaining in today's backlog. A newly estimated cancellation tail can justify a forecast residual adjustment, but applying a full lifetime cancellation rate to a net forecast would mix denominators. [Q2 2026 10-Q](https://www.sec.gov/Archives/edgar/data/1559720/000155972026000027/abnb-20260630.htm)

The historical seasonal sample includes the 2025 rollout/product step. Removing 2025 descriptively gives 8.808% Q3 and 9.983% Q4 before overlays—0.684 and 0.636 points below the three-year model. This is only two observations, not an RNPL causal estimate. It demonstrates baseline sensitivity and the need to reconcile the lap against the product contribution embedded in the selected baseline. Including 2025 and adding a lap adjustment is not inherently invalid; the existing overlay simply does not calculate that reconciliation.

The saved consensus file contains no retrievable Q3 nights consensus. Its final row explicitly records that gap. Management's low-double-digit wording is encoded as 10–12% by the researchers; 10–12 is not a numeric company guidance range or verified sell-side consensus. Do not describe 9.99 versus 10.00 as a meaningful guidance miss: it is below the model's chosen boundary by rounding-scale precision.

## 2. Rollout evidence and unknowns

| Period | Verified disclosure | Denominator / limitation |
|---|---|---|
| Q2 2025 call | No named US RNPL testing/launch established in the bounded search | Generic payment or Brazil installment comments do not establish US treatment |
| Q3 2025 | Management described beginning-Q3 launch; US guests, domestic stays, flexible/moderate policies; approximately 70% take-up when offered | Conditional adoption, not percentage of all guests, listings or nights |
| August 14, 2025 | Public US announcement | Announcement date differs from treatment start; precise ramp not disclosed |
| Q4 2025 / February 2026 call | Approximate platform cancellation rate moved from 16% historically to 17%; RNPL cohorts higher; management said tests remained net beneficial through check-in | No night-weighted cohort denominator, RNPL-only rate, or cancellation timing series |
| February 17, 2026 | Global domestic/international availability on eligible listings; announcement excludes BRL/INR/TRY reservations | Global availability does not mean universal eligibility; currency exceptions matter for controls |
| Q1 2026 | Roughly 20% of global GBV from RNPL; three product changes combined supplied approximately 3 points nights / 4 points GBV growth | GBV share is not nights share; growth contribution is not RNPL-only |
| Q2 2026 SEC letter | Broader listings/countries and more prominence in booking journey | Confirms continued expansion, but no quarterly eligibility percentage |
| Q2 call as reproduced by transcript vendors | Over 20% of Q2 GBV; eligible booking types expanded in July | Call-mirror evidence, not independently recovered from official call PDF in this pass; exact new types and ramp not disclosed |

Public sources: [Q2 2025 call](https://s26.q4cdn.com/656283129/files/doc_financials/2025/q2/Airbnb-Q2-25-Earnings-Call-Transcript.pdf); [Q3 2025 call](https://s26.q4cdn.com/656283129/files/doc_financials/2025/q3/CORRECTED-TRANSCRIPT_-Airbnb-Inc-ABNB-US-Q3-2025-Earnings-Call-6-November-2025-5_00-PM-ET.pdf); [US announcement](https://news.airbnb.com/reserve-now-pay-later); [Q4 2025 call](https://s26.q4cdn.com/656283129/files/doc_financials/2025/q4/Airbnb-Q4-25-Earnings-Call-Transcript.pdf); [global announcement](https://news.airbnb.com/reserve-now-pay-later-is-now-available-worldwide); [Q1 2026 call](https://s26.q4cdn.com/656283129/files/doc_financials/2026/q1/Airbnb-Q1-26-Earnings-Call-Transcript.pdf); [Q2 SEC letter](https://www.sec.gov/Archives/edgar/data/1559720/000119312526337928/d70413dex991.htm); [Q2 call mirror](https://www.roic.ai/quote/ABNB:US/transcripts/2026-year/2-quarter).

Platform-wide quarterly eligibility percentages, night-weighted take-up, outstanding RNPL nights, remaining cancellation probabilities, and cancellation-month distributions are all unknown. They should remain unknown fields, not be filled by straight-line interpolation between the public percentages. The approximate Q4 cancellation comment and Q1 GBV share are different vintages and denominators.

## 3. What a material effect requires

[Reproducible materiality tables](materiality.md) and [machine-readable scenarios](materiality.json) were generated by `analysis/src/rnpl_materiality.py`. The script validates 2025 denominators against the repository KPI panel and checks the probability-to-loss identities. It does not fit an RNPL forecast.

| Incremental growth reduction | Q3 net lost nights | Q4 net lost nights |
|---|---:|---:|
| 1 point | 1.336 million | 1.219 million |
| 2 points | 2.672 million | 2.438 million |
| 3 points | 4.008 million | 3.657 million |

For example, at an assumed 40 million live RNPL nights, reducing Q3 growth one point requires an additional 3.34-point probability of cancellation during Q3, beyond the forecast's assumed remaining risk. If 25% of excess canceled nights is offset by incremental net replacement bookings recognized in Q3, the required revision rises to 4.45 points. A two-point growth reduction requires 6.68 or 8.91 points, respectively. These are hypothetical exposures and offsets, not measurements.

Define the snapshot date. A July 1 opening-backlog calculation is different from a September 10 remaining-quarter forecast. H1 gross RNPL bookings cannot be treated as live September exposure: many have already stayed or canceled. Also include cancellations of bookings made after the snapshot in a full quarterly forecast; the simple exposure table only covers the live cohort.

An RNPL/no-RNPL comparison must model both 2025 and 2026. A forecast revision with the 2025 reported denominator fixed only requires an incremental 2026 numerator revision. The sensitivity tables implement the latter.

## 4. Existing-data audit and stop/go decision

The aggregate booking curves are not the entire local inventory. The audit found historical raw calendars that were not represented in the earlier single-snapshot analysis.

| Dataset | Coverage verified in this pass | What it can establish |
|---|---|---|
| `data/raw/inside_airbnb_calendar/` | 164 compressed calendar files, 34 markets; 32 markets have five snapshots, Bogota and Sao Paulo two. Filename dates span August 31, 2025–August 31, 2026 | Repeated listing/stay-date availability, subject to actual row overlap; potential reopening/refilling proxy |
| `data/processed/booking_curve_daily.csv` | 44,379 rows, 120 markets, 24 distinct capture dates across markets, June 14–August 10, 2026 | Aggregate unavailable-date rates at forward horizons; not repeated captures of every market |
| `data/processed/booking_curves_by_market.csv` | 600 rows, five horizon buckets per market | Descriptive snapshot curves; no reservation events |
| Theo legacy `processed/airbnb_quant_panel_v1/calendar_daily.csv.gz` | Manifest reports 5,816,795 rows / 160.6 MB; sampled header/source identifies legacy San Francisco mirror, 2019–2020 | Not an RNPL-era history |
| `data/raw/booking/` | Hotel-review and training-user files | No Airbnb reservation-event ledger |
| `data/manifests/inside_airbnb_download_log.csv` | Current acquisition log includes 92 calendar acquisitions | Does not fully document the broader 164-file historical directory; provenance reconciliation needed before publishing estimates |

The parent independently verified the 164-file/34-market inventory, per-market snapshot counts, date endpoints, and three Austin headers. [Coverage by market and sampled schemas](calendar_inventory.json). This was an inventory/header audit, not a complete parsing or integrity validation of the raw files.

The stable useful columns in the sampled headers are `listing_id`, `date`, `available`, and minimum/maximum nights. Price fields exist in the sampled September 2025 file but are absent in the December/March samples. There are no reservation IDs, booking/cancellation timestamps, guest payment events, RNPL flags, or guest origins in those headers.

Most historical captures are approximately quarterly, followed by an August update. An unavailable date that reopens between captures is not proven canceled; host blocks, other-channel activity, changing supply, and minimum-stay restrictions confound the interpretation. Cancellation followed by rebooking between snapshots is invisible. Therefore reopening rates are neither an unbiased cancellation estimate nor a strict cancellation lower bound without assumptions about host blocks.

The earliest files are already after the initial US launch, so this directory does not supply a clean US prelaunch baseline or a full 2024 comparison. Some non-US markets have pre-February-2026 snapshots, but guest origin and eligibility are missing. That permits descriptive timing comparisons, not clean RNPL treatment identification. Five snapshots also do not guarantee five observations of a given stay date: historical dates exit the forward calendar horizon. Stay-date overlap must be measured before computing any transition.

**Go:** a small pilot on Austin and two non-US markets with five vintages, first reconciling source URLs/hashes, then stable listing IDs and identical future stay dates. Tabulate observed reopening/refilling by days to arrival, original availability, listing stability, and minimum-stay changes. Its first output is data coverage and robustness of the proxy, not a platform cancellation haircut. Choose the non-US markets after confirming row overlap; do not select on the strongest apparent result.

**No-go with current files:** an empirical RNPL cancellation probability, a causal RNPL contribution, or a defensible conversion from reopening counts into global lost nights. Reservation events and exposure information remain necessary for that step. Beginning a daily collection now would help future research, but would not reconstruct the missing 2025 history for this quarter's forecast.

## Next data request, drafted for field feasibility

Request a small anonymized sample and field dictionary first; no outreach was sent. Ask whether the provider can supply reservation events from January 2024 through September 2026, including canceled records and future scheduled stays, with:

- Stable anonymized booking and listing IDs; channel; destination; guest-origin country and booking currency if available.
- Creation timestamp, original and revised stay dates/nights, cancellation timestamp and canceled nights, status and reason.
- Cancellation policy at booking, not just today's listing policy.
- RNPL offered/eligible and chosen flags; guest payment due/paid/failed dates if recorded. Host payout dates cannot substitute for guest payment dates.
- Historical snapshots or an event log sufficient to reconstruct the live backlog at each forecast date; extraction cutoff and revision policy.
- Stable panel membership and listing characteristics; a way to observe subsequent replacement reservations.

Minimum go/no-go: dates and canceled records are needed for any survival analysis; RNPL/eligibility flags or credible historical assignment are needed for RNPL attribution. If the provider lacks those fields, a panel can still diagnose Airbnb cancellation deterioration, but cannot isolate RNPL from policy changes. Do not ask for payment credentials or personally identifying guest data.

The first empirical deliverable should be matched, night-weighted conditional cancellation curves and cancellation-month allocation—not a headline regression of unavailable calendars on a rollout dummy. Separate booking conversion uplift, booking pull-forward, and cancellation survival so that the same effect is not subtracted twice.

