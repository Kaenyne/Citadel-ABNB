# Hotel funnel audit: defined 25-market sample

Prepared 2026-09-07. The sample retains 13 existing markets and adds 12 explicitly
selected extensions. It is a judgment-selected analytical scope, not a recovered
prior team list or a representative global sample. Austin is excluded from pooled
growth under inherited coverage flags: 25 evidence rows, 24 comparable pairs.

Read the [operating audit](../../../research/notes/2026-09-07_hotel-funnel-audit.md).

| File | Meaning |
|---|---|
| `hotel_25_market_audit.csv` | Joined 25-market selection, capacity evidence and strict hotel-tagged listing outcomes |
| `archive25/hotel_listing_panel.csv` | 25 markets x 3 taxonomies; September 2025 to June 2026 capture starts |
| `archive25/hotel_panel_pooled.csv` | 24 comparable markets; ratio-of-sums changes, not annualized |
| `archive25/reused_capture_manifest.csv` | 50 existing files with verified hashes and row counts |
| `archive25/hotel_taxonomy.csv` | Endpoint property-type counts |
| `archive25/methodology.json` | Scope hash, taxonomy, duplicate-ID check and measurement limits |
| `hotel_listing_panel.csv`, `hotel_panel_pooled.csv` | Separate original 13-market sensitivity (12 usable), extending to late August/early September 2026; never combined with the 25-market pool |
| `reused_capture_manifest.csv` | 26 existing captures for the original sensitivity |
| `unique_reused_captures.csv`, `panel_capture_overlap.json` | 76 capture references, 64 unique hashes, 12 captures shared; no new Inside Airbnb download |
| `hotel_market_capacity_anchors.csv` | All 25 evidence rows, dated definitions and explicit gaps; independent-room estimates identified in two cities |
| `verified_spreadsheet_anchors.csv` | Reconciled Madrid hotel categories and Buenos Aires boutique properties/available room nights |
| `global_hotel_tam_sensitivity.csv` | Global unbranded-room proxy; assumed occupancy and channel share |
| `hotel_mix_scenarios.csv` | Mathematical mix scenarios, not hotel guidance |
| `hotel_supply_requirements.csv` | Required sign-ups under explicit activation/timing/productivity assumptions |
| `hotel_credit_sensitivity.csv` | Economic incentive sensitivity, not GAAP accounting forecast |
| `hotel_model_summary.json` | Input hash, computed boundaries and limitations |
| `team_review_manifest.csv`, `team_review_urls.csv` | Frozen visible GitHub main/local/ZIP evidence and source references |
| `public_source_overlap.csv`, `overlap_review_metadata.json` | Exact URL reuse, semantic disposition and review boundary |

Editable [assumptions](../../../analysis/config/hotel_funnel_audit.json),
[market selection](../../../analysis/config/hotel_markets_25.csv) and
[31-source ledger](../../../research/sources/hotel_funnel_audit.json).
Unknown room counts and independent shares remain missing, never imputed from a
world average. The heterogeneous city anchors are not summed. Listing IDs are not
properties or physical rooms; reviews and blocked calendars are not booked nights.

Missing review values are unknown, not zero. A review total is blank if any listing
in that cohort has a missing value; its growth and reviews-per-listing measures
remain blank too, including pooled and retained-ID comparisons. `_observed_sum`
columns preserve the sum of known counts and `_missing` columns count missing
listing values. Reported zeros remain zero; percentage growth from a zero baseline
is undefined. The dated narrative/chart generator stops if review fields are
missing, so its existing conclusions cannot be published over incomplete inputs.

The official Buenos Aires source reports available room nights, not physical keys:
34,348 in March 2026 / 31 days = 1,108 average daily available boutique rooms across
44 establishments. Cape Town's 89 named example units are not city TAM. Rio's
unverified historical capacity lead is excluded from numerical room anchors.

Raw review copies and public verification downloads remain in ignored
`data/raw/hotel_funnel_audit/`. Existing listing data are attributed to
[Inside Airbnb](https://insideairbnb.com/get-the-data/) under CC BY 4.0.
Focused tests and the spreadsheet reconciliations pass; replay commands are
in the operating audit. No claims of private/unshared team-work coverage or causal
hotel acquisition effects are made.
