# Transaction data needed to complete the regulatory earnings model

No message has been sent to a vendor or to Airbnb. This specifies the usable export required from existing access.

## Minimum export

One row per listing, platform and stay month, preferably January 2022 through the latest completed month. Include every listing observed during the window, even if it later disappeared. Export Spain nationally with city/municipality fields; NYC plus nearby New Jersey/Long Island markets; and Maui plus other Hawaiian counties. The same specification supports the other jurisdictions in the original register.

| Field | Why it is needed |
|---|---|
| `platform`, `listing_id`, `canonical_property_id`, `unit_id` | Isolate Airbnb bookings and deduplicate relisted or cross-listed inventory. |
| `stay_month`, `booking_month`, `data_vintage`, `observation_status` | Separate stayed revenue from forward bookings, revisions and missing observations. |
| `municipality`, `district`, `latitude`, `longitude` | Match policy boundaries and destination spillovers. Flag coordinate precision. |
| `licence_id`, `parcel_id`, `licence_valid_from`, `licence_valid_to`, `licence_status` | Join regulatory scope to the listing as it existed at the event date. |
| `first_seen`, `last_seen`, `delisted_date`, `delisting_reason`, `replacement_listing_id` | Distinguish enforcement removals, normal churn, relisting and genuine zeros. |
| `listing_type`, `primary_residence`, `hotel_status`, `minimum_nights`, `grandfathered`, `exemption_status` | Identify the actual legal cohort. Unknown must remain unknown. |
| `booked_listing_nights`, `guest_nights`, `bookings`, `cancelled_nights`, `available_nights`, `blocked_nights` | Measure demand and capacity without treating owner blocks as bookings. |
| `realized_room_revenue`, `cleaning_fee`, `guest_fee`, `host_fee`, `taxes`, `refunds`, `currency` | Reconcile the correct fee base; avoid applying a take rate to host net income or a fee-inclusive price. |
| `data_method`, `coverage_fraction`, `revision_flag` | Distinguish observed transactions from vendor estimates and methodological changes. |

A market-level monthly series is useful if listing-level access is unavailable, but cannot identify whether regulated properties were the ones that lost bookings. Check the subscription's export rights before assuming an API key includes these fields.

## Required checks before estimating an effect

1. Reconcile listing counts and monthly totals to the vendor dashboard, using the same activity definition and data vintage. Preserve numeric listing IDs as strings.
2. Keep missing observations separate from zero bookings. Treat a delisting as an exit only when the panel covers that listing and month. Remove duplicates using property/unit identity, not shared host identity.
3. Match legal scope as of the event date. For Barcelona, reconcile current validity and licence counts. For Maui, resolve the latest amendments, parcel portions, timeshares and unit-specific exemptions. For Spain, obtain the removed-ad ID list or an explicitly identified vendor enforcement cohort.
4. Use at least 12–24 pre-event months and a full seasonal post-event window where available. Fit and inspect pre-trends. Model NYC's September 2023 enforcement and Spain's successive 2025 events separately. Maui and Barcelona currently support prospective exposure, not post-deadline causal tests.
5. Treat adjacent destinations and alternative stay types as potential recapture outcomes. A control receiving displaced demand biases a difference-in-differences estimate. Check unaffected destinations and placebo dates.
6. Translate lost room/booking value to Airbnb fees on a consistent base. Estimate ADR/mix changes on surviving properties. Separate incremental compliance/marketing expense from variable contribution lost.
7. Bridge only the incremental change absent from the investment model's baseline into each forecast year. Keep the result separate from any already embedded historical effect and from contingent fines.

The current SQLite crosswalk tables supply the listing IDs for the first two matched cohorts. Actual booked nights, revenue, primary-residence status, transaction-level recapture and definitive exemptions remain unfilled rather than imputed as facts.
