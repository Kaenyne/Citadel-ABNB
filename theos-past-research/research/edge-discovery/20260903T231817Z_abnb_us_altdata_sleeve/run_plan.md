# U.S. alternative-data sleeve — governed run plan

Run ID: `20260903T231817Z_abnb_us_altdata_sleeve`

## Agent hierarchy and ownership

1. **ABNB Research Orchestrator** — main Codex task; owns user communication and final decision.
2. **abnb_alt_data** — research lead; owns source governance, canonical registries, hypothesis freeze, point-in-time reconciliation, target alignment, and combined artifacts.
3. **physical_world_activity_edge** — national and multi-city U.S. travel-activity sources; lane-local files only.
4. **supply_scarcity_web_edge** — accommodation demand/pricing and public STR supply/regulatory sources; lane-local files only.

No other agent may be launched. The two lanes may not edit canonical registries or inspect ABNB guidance outcomes.

## Scope

Three source families are authorized for discovery and the smallest lawful historical collection:

1. Nationwide or multi-city U.S. travel activity.
2. Nationwide accommodation demand and pricing.
3. Multi-city official STR supply and regulatory activity.

Only free, public, official sources are in scope. Paid data, trials, credentials, controlled properties, Airbnb-controlled sources, OTAs, commercial booking engines, PII, CAPTCHA/access-control bypass, and ambiguous automated access are out of scope.

## Governance sequence

1. Register each source canonically before its first network request.
2. Register each official permission-reconnaissance request before execution.
3. Cache terms, robots, license, documentation, metadata, and publication-calendar responses.
4. Reconstruct the exact data-path `ScrapeCandidate` and run `assess_scrape_candidate`.
5. Collect data only when `allowed=true`, beginning with the smallest useful request and observing the provider limit or ten requests per minute, whichever is stricter.
6. Freeze no more than six versioned hypotheses across the three families before the lead reads collected values or aligns them to outcomes.
7. Preserve all blocked, missing, current-snapshot, and prospective-only rows.

## Normalized long schema

The combined `observations_long.csv` will contain at least:

`observation_id, source_id, provider, series_id, metric, reference_period, geography, unit, value, observation_at_utc, first_available_at_utc, revision_at_utc, vintage_at_utc, collected_at_utc, pit_treatment, strict_pit_eligible, raw_file, raw_sha256, source_url, permission_status, exclusion_reason`.

Current-history values without a verified contemporaneous publication artifact are retained with `strict_pit_eligible=false`; they are never backfilled as historical vintages.

## Event alignment

The fixed target table is `research/forecasting/runs/20260903T224632Z_50_source_guidance_format/guidance_history.csv`. The combined `event_aligned_features.csv` will contain at least:

`prediction_id, source_id, hypothesis_id, guidance_cutoff_at_utc, latest_eligible_reference_period, feature_value, feature_transform, expected_direction, strict_eligibility, exclusion_reason, guidance_midpoint, prior_year_comparable_midpoint, guidance_yoy_or_change`.

Eligibility requires `first_available_at_utc < guidance_cutoff_at_utc`; equality fails. Features and expected directions are frozen before values are inspected. Comparisons are descriptive fixed-rule audits, not regression, correlation search, feature selection, threshold optimization, or evidence of alpha.

## Stop condition

The run ends after the validated long-form sleeve, event alignment, descriptive comparison, permission/source manifests, and limitations memo. It does not begin a predictive-model or quant phase.
