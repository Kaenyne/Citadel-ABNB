# H-012 v2 revenue-weighted blend recommendation

## Recommended fixed weight

Use **50.4454% U.S. activity and 49.5546% Europe proxy activity**:

```text
composite = 0.5044535261 × U.S. activity growth
          + 0.4955464739 × EU27 platform-night growth
```

The weights are derived mechanically from Airbnb's audited 2025 listing-location revenue:

- United States revenue: $4,814 million.
- EMEA revenue: $4,729 million.
- Covered-sleeve denominator: $9,543 million.
- U.S. weight: 4,814 / 9,543 = 0.5044535261.
- Europe-proxy weight: 4,729 / 9,543 = 0.4955464739.

The authoritative source is Airbnb's Form 10-K for the year ended December 31, 2025, SEC accession `0001559720-26-000004`, accepted `2026-02-12T21:04:39Z`. The filing reports revenue by geographic region and separately reports U.S. revenue; both tables attribute revenue by the location of the host's listing. The reviewed SEC response was 2,131,290 bytes with SHA-256 `61bac47250511a2263631ebd99e92b1d42caf305d27ba9d9fbfa7b11aa199c02`.

Official filing: https://www.sec.gov/Archives/edgar/data/1559720/000155972026000004/abnb-20251231.htm

## Why this is the best available mapping

The U.S. side uses an exact Airbnb U.S. revenue disclosure rather than North America. Airbnb does not disclose Europe-only revenue; EMEA is therefore the closest official revenue proxy for the EU27 feature. This mapping is geographically closer than the alternative same-table North America/EMEA blend, which would yield 52.3526% North America and 47.6474% EMEA.

The two selected categories represent 77.9593% of Airbnb's 2025 global revenue. The normalization deliberately excludes Latin America and Asia Pacific rather than silently assigning their exposure to either sleeve.

## Point-in-time treatment

The weight is not eligible for any guidance cutoff on or before `2026-02-12T21:04:39Z`. Applying it to earlier events is an ex-post diagnostic. It is available before the May and August 2026 guidance events in the current panel, but those composite rows still fail strict PIT eligibility because the underlying SFO and Eurostat histories are current snapshots without original vintages.

The fixed pair-normalized U.S. share changes from 54.2694% in 2023 to 52.8775% in 2024 and 50.4454% in 2025. This 3.824 percentage-point movement is material evidence that annual geographic mix drifts. The 2025 weight should therefore be frozen only for this explicitly authorized diagnostic, not portrayed as the historical mix at 2021-2025 cutoffs.

## Usability score

The disclosure-derived weight scores **74/100 for historical use**:

- Authority and auditability: 5/5.
- Revenue-target definition match: 5/5.
- U.S. geographic match: 5/5.
- Europe proxy match: 3/5 because EMEA is broader than Europe/EU27.
- Covered revenue: 4/5 because the pair covers 77.96% of global revenue.
- Temporal stability: 3/5 because the normalized mix moved materially over 2023-2025.
- Frequency and recency: 2/5 because disclosure is annual.
- Historical PIT availability: 1/5 because the selected filing was accepted in February 2026.

For prospective use after the filing date, the weight source alone would score 82/100 if PIT availability is raised to 5/5. That does not cure vintage failures in the underlying signals.

## Governance decision

H-012 v2 supersedes the 50/50 diagnostic for this continuation but does not overwrite H-012 v1. The weight was selected solely from audited revenue disclosures and was frozen before the v2 outcome calculation. No weight, window, threshold, source, or lag was fitted to guidance outcomes.

Decision: `WATCH_PROSPECTIVELY`. No alpha or predictive-power claim.

